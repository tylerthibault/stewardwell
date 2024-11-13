from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.modules.homeconomy import bp
from app.modules.homeconomy.models import Chore, CompletedChore, Reward, ClaimedReward, Goal
from app.utils.logger import ActivityLogger
from datetime import datetime

activity_logger = ActivityLogger('homeconomy')


@bp.route('/parent/dashboard')
@login_required
def parent_dashboard():
    """Parent's dashboard view"""
    if not current_user.user_type == 'parent':
        flash('Access denied. Parents only.', 'error')
        return redirect(url_for('main.index'))

    # Get all family chores
    chores = Chore.query.filter_by(
        family_id=current_user.family_id,
        is_active=True
    ).all()

    # Get pending chore verifications
    pending_verifications = CompletedChore.query.join(Chore).filter(
        Chore.family_id == current_user.family_id,
        CompletedChore.verified == False
    ).all()

    # Get active rewards
    rewards = Reward.query.filter_by(
        family_id=current_user.family_id,
        is_active=True
    ).all()

    # Get active goals
    goals = Goal.query.filter_by(
        family_id=current_user.family_id,
        is_active=True
    ).all()

    # Get children's progress
    children = current_user.family.members.filter_by(user_type='child').all()

    activity_logger.log_activity(
        current_user.id,
        'parent_dashboard_view',
        {
            'total_chores': len(chores),
            'pending_verifications': len(pending_verifications),
            'active_rewards': len(rewards),
            'active_goals': len(goals)
        }
    )

    return render_template('homeconomy/parent/dashboard.html',
                         title='Parent Dashboard',
                         chores=chores,
                         pending_verifications=pending_verifications,
                         rewards=rewards,
                         goals=goals,
                         children=children)

@bp.route('/child/dashboard')
@login_required
def child_dashboard():
    """Child's dashboard view"""
    if not current_user.user_type == 'child':
        flash('Access denied. Children only.', 'error')
        return redirect(url_for('main.index'))

    # Get available chores (not completed or verified)
    completed_chore_ids = [c.chore_id for c in current_user.completed_chores.filter_by(verified=False).all()]
    available_chores = Chore.query.filter(
        Chore.family_id == current_user.family_id,
        Chore.is_active == True,
        ~Chore.id.in_(completed_chore_ids) if completed_chore_ids else True
    ).filter(
        (Chore.assigned_to == None) | (Chore.assigned_to == current_user.id)
    ).all()

    # Get available rewards
    available_rewards = Reward.query.filter(
        Reward.family_id == current_user.family_id,
        Reward.is_active == True,
        (Reward.quantity > 0) | (Reward.quantity == -1)  # -1 means unlimited
    ).all()

    # Get active family goals
    active_goals = Goal.query.filter_by(
        family_id=current_user.family_id,
        is_active=True
    ).all()

    activity_logger.log_activity(
        current_user.id,
        'child_dashboard_view',
        {
            'available_chores': len(available_chores),
            'available_rewards': len(available_rewards),
            'active_goals': len(active_goals)
        }
    )

    return render_template('homeconomy/child/dashboard.html',
                         title='My Dashboard',
                         chores=available_chores,
                         rewards=available_rewards,
                         goals=active_goals)
