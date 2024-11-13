from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.modules.homeconomy import bp
from app.modules.homeconomy.forms import (
    FamilyForm, ChoreForm, RewardForm, GoalForm,
    VerifyChoreForm, ClaimRewardForm, FulfillRewardForm,
    AddChildForm, JoinFamilyForm
)
from app.modules.homeconomy.models import (
    Chore, CompletedChore, Reward, ClaimedReward,
    Goal
)
from app.models.user import User, Family
from app.utils.logger import log_action, ActivityLogger
from datetime import datetime

# Initialize activity logger for homeconomy module
activity_logger = ActivityLogger('homeconomy')

def is_parent():
    return current_user.user_type == 'parent'

def is_child():
    return current_user.user_type == 'child'

@bp.route('/')
@login_required
@log_action('homeconomy_index')
def index():
    if is_parent():
        return redirect(url_for('homeconomy.parent_dashboard'))
    return redirect(url_for('homeconomy.child_dashboard'))

# Parent Routes
@bp.route('/parent/dashboard')
@login_required
@log_action('parent_dashboard_view')
def parent_dashboard():
    if not is_parent():
        activity_logger.log_error(
            current_user.id,
            'unauthorized_access',
            'Non-parent user attempted to access parent dashboard'
        )
        flash('Access denied. Parents only.', 'error')
        return redirect(url_for('homeconomy.index'))
    
    return render_template('homeconomy/parent/dashboard.html',
                         title='Parent Dashboard')

@bp.route('/family/create', methods=['GET', 'POST'])
@login_required
@log_action('family_creation')
def create_family():
    if not is_parent():
        activity_logger.log_error(
            current_user.id,
            'unauthorized_access',
            'Non-parent user attempted to create family'
        )
        flash('Access denied. Parents only.', 'error')
        return redirect(url_for('homeconomy.index'))
    
    if current_user.family:
        activity_logger.log_error(
            current_user.id,
            'duplicate_family',
            'User attempted to create multiple families'
        )
        flash('You already have a family.', 'error')
        return redirect(url_for('homeconomy.parent_dashboard'))
    
    form = FamilyForm()
    if form.validate_on_submit():
        family = Family(
            name=form.name.data,
            owner_id=current_user.id
        )
        current_user.family = family
        db.session.add(family)
        db.session.commit()
        
        activity_logger.log_activity(
            current_user.id,
            'family_created',
            {'family_name': family.name, 'family_id': family.id}
        )
        flash(f'Family {family.name} created successfully!', 'success')
        return redirect(url_for('homeconomy.parent_dashboard'))
    
    return render_template('homeconomy/family/create.html', form=form)

@bp.route('/family/<int:family_id>/add_child', methods=['GET', 'POST'])
@login_required
@log_action('add_child')
def add_child(family_id):
    if not is_parent():
        activity_logger.log_error(
            current_user.id,
            'unauthorized_access',
            'Non-parent user attempted to add child'
        )
        flash('Access denied. Parents only.', 'error')
        return redirect(url_for('homeconomy.index'))
    
    family = Family.query.get_or_404(family_id)
    if family.owner_id != current_user.id:
        activity_logger.log_error(
            current_user.id,
            'unauthorized_access',
            f'User attempted to add child to another family: {family_id}'
        )
        flash('Access denied. Not your family.', 'error')
        return redirect(url_for('homeconomy.index'))
    
    form = AddChildForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            activity_logger.log_error(
                current_user.id,
                'duplicate_username',
                f'Attempted to create child with existing username: {form.username.data}'
            )
            flash('Username already exists. Please choose a different one.', 'error')
            return render_template('homeconomy/family/add_child.html', form=form, family=family)
        
        child = User(
            username=form.username.data,
            email=form.email.data if form.email.data else None,
            user_type='child',
            family_id=family.id,
            created_at=datetime.utcnow()
        )
        child.set_password(form.password.data)
        db.session.add(child)
        
        try:
            db.session.commit()
            activity_logger.log_activity(
                current_user.id,
                'child_added',
                {
                    'child_username': child.username,
                    'child_id': child.id,
                    'family_id': family.id
                }
            )
            flash(f'Child {child.username} added successfully!', 'success')
            return redirect(url_for('homeconomy.parent_dashboard'))
        except Exception as e:
            db.session.rollback()
            activity_logger.log_error(
                current_user.id,
                'database_error',
                f'Error adding child: {str(e)}'
            )
            flash('An error occurred while adding the child. Please try again.', 'error')
            return render_template('homeconomy/family/add_child.html', form=form, family=family)
    
    return render_template('homeconomy/family/add_child.html', form=form, family=family)

@bp.route('/chores/create', methods=['GET', 'POST'])
@login_required
@log_action('create_chore')
def create_chore():
    if not is_parent():
        activity_logger.log_error(
            current_user.id,
            'unauthorized_access',
            'Non-parent user attempted to create chore'
        )
        flash('Access denied. Parents only.', 'error')
        return redirect(url_for('homeconomy.index'))
    
    if not current_user.family:
        activity_logger.log_error(
            current_user.id,
            'no_family',
            'User attempted to create chore without a family'
        )
        flash('You need to create a family first.', 'error')
        return redirect(url_for('homeconomy.create_family'))
    
    form = ChoreForm(family=current_user.family)
    if form.validate_on_submit():
        chore = Chore(
            name=form.name.data,
            description=form.description.data,
            coins_reward=form.coins_reward.data,
            points_reward=form.points_reward.data,
            frequency=form.frequency.data,
            family_id=current_user.family.id,
            assigned_to=form.assigned_to.data if form.assigned_to.data != 0 else None
        )
        db.session.add(chore)
        db.session.commit()
        
        activity_logger.log_activity(
            current_user.id,
            'chore_created',
            {
                'chore_name': chore.name,
                'chore_id': chore.id,
                'coins_reward': chore.coins_reward,
                'points_reward': chore.points_reward,
                'assigned_to': chore.assigned_to
            }
        )
        flash(f'Chore {chore.name} created successfully!', 'success')
        return redirect(url_for('homeconomy.parent_dashboard'))
    
    return render_template('homeconomy/chores/create.html', form=form)

@bp.route('/chores/<int:chore_id>/verify', methods=['GET', 'POST'])
@login_required
@log_action('verify_chore')
def verify_chore(chore_id):
    if not is_parent():
        activity_logger.log_error(
            current_user.id,
            'unauthorized_access',
            'Non-parent user attempted to verify chore'
        )
        flash('Access denied. Parents only.', 'error')
        return redirect(url_for('homeconomy.index'))
    
    completed_chore = CompletedChore.query.get_or_404(chore_id)
    if completed_chore.chore.family_id != current_user.family.id:
        activity_logger.log_error(
            current_user.id,
            'unauthorized_access',
            f'User attempted to verify chore from another family: {chore_id}'
        )
        flash('Access denied. Not your family.', 'error')
        return redirect(url_for('homeconomy.index'))
    
    form = VerifyChoreForm()
    if form.validate_on_submit():
        if form.verified.data:
            completed_chore.verified = True
            completed_chore.verified_at = datetime.utcnow()
            completed_chore.verified_by_id = current_user.id
            
            # Award coins and points
            child = User.query.get(completed_chore.child_id)
            child.coins += completed_chore.chore.coins_reward
            current_user.family.total_points += completed_chore.chore.points_reward
            
            db.session.commit()
            
            activity_logger.log_activity(
                current_user.id,
                'chore_verified',
                {
                    'chore_id': completed_chore.chore_id,
                    'child_id': completed_chore.child_id,
                    'coins_awarded': completed_chore.chore.coins_reward,
                    'points_awarded': completed_chore.chore.points_reward
                }
            )
            flash('Chore verified and rewards distributed!', 'success')
        return redirect(url_for('homeconomy.parent_dashboard'))
    
    return render_template('homeconomy/chores/verify.html', 
                         form=form, completed_chore=completed_chore)

@bp.route('/rewards/create', methods=['GET', 'POST'])
@login_required
@log_action('create_reward')
def create_reward():
    if not is_parent():
        activity_logger.log_error(
            current_user.id,
            'unauthorized_access',
            'Non-parent user attempted to create reward'
        )
        flash('Access denied. Parents only.', 'error')
        return redirect(url_for('homeconomy.index'))
    
    if not current_user.family:
        activity_logger.log_error(
            current_user.id,
            'no_family',
            'User attempted to create reward without a family'
        )
        flash('You need to create a family first.', 'error')
        return redirect(url_for('homeconomy.create_family'))
    
    form = RewardForm()
    if form.validate_on_submit():
        reward = Reward(
            name=form.name.data,
            description=form.description.data,
            coin_cost=form.coin_cost.data,
            quantity=form.quantity.data,
            family_id=current_user.family.id,
            is_active=form.is_active.data
        )
        db.session.add(reward)
        db.session.commit()
        
        activity_logger.log_activity(
            current_user.id,
            'reward_created',
            {
                'reward_name': reward.name,
                'reward_id': reward.id,
                'coin_cost': reward.coin_cost,
                'quantity': reward.quantity
            }
        )
        flash(f'Reward {reward.name} created successfully!', 'success')
        return redirect(url_for('homeconomy.parent_dashboard'))
    
    return render_template('homeconomy/rewards/create.html', form=form)

@bp.route('/goals/create', methods=['GET', 'POST'])
@login_required
@log_action('create_goal')
def create_goal():
    if not is_parent():
        activity_logger.log_error(
            current_user.id,
            'unauthorized_access',
            'Non-parent user attempted to create goal'
        )
        flash('Access denied. Parents only.', 'error')
        return redirect(url_for('homeconomy.index'))
    
    if not current_user.family:
        activity_logger.log_error(
            current_user.id,
            'no_family',
            'User attempted to create goal without a family'
        )
        flash('You need to create a family first.', 'error')
        return redirect(url_for('homeconomy.create_family'))
    
    form = GoalForm()
    if form.validate_on_submit():
        goal = Goal(
            name=form.name.data,
            description=form.description.data,
            points_required=form.points_required.data,
            family_id=current_user.family.id,
            is_active=form.is_active.data
        )
        db.session.add(goal)
        db.session.commit()
        
        activity_logger.log_activity(
            current_user.id,
            'goal_created',
            {
                'goal_name': goal.name,
                'goal_id': goal.id,
                'points_required': goal.points_required
            }
        )
        flash(f'Goal {goal.name} created successfully!', 'success')
        return redirect(url_for('homeconomy.parent_dashboard'))
    
    return render_template('homeconomy/goals/create.html', form=form)

# Child Routes
@bp.route('/child/dashboard')
@login_required
@log_action('child_dashboard_view')
def child_dashboard():
    if not is_child():
        activity_logger.log_error(
            current_user.id,
            'unauthorized_access',
            'Non-child user attempted to access child dashboard'
        )
        flash('Access denied. Children only.', 'error')
        return redirect(url_for('homeconomy.index'))
    
    available_chores = Chore.query.filter(
        (Chore.family_id == current_user.family_id) &
        (Chore.is_active == True) &
        ((Chore.assigned_to == None) | (Chore.assigned_to == current_user.id))
    ).all()
    
    available_rewards = Reward.query.filter_by(
        family_id=current_user.family_id,
        is_active=True
    ).all()
    
    active_goals = Goal.query.filter_by(
        family_id=current_user.family_id,
        is_active=True
    ).all()
    
    return render_template('homeconomy/child/dashboard.html',
                         chores=available_chores,
                         rewards=available_rewards,
                         goals=active_goals)

@bp.route('/chores/<int:chore_id>/complete', methods=['POST'])
@login_required
@log_action('complete_chore')
def complete_chore(chore_id):
    if not is_child():
        activity_logger.log_error(
            current_user.id,
            'unauthorized_access',
            'Non-child user attempted to complete chore'
        )
        return jsonify({'error': 'Access denied. Children only.'}), 403
    
    chore = Chore.query.get_or_404(chore_id)
    if chore.family_id != current_user.family_id:
        activity_logger.log_error(
            current_user.id,
            'unauthorized_access',
            f'User attempted to complete chore from another family: {chore_id}'
        )
        return jsonify({'error': 'Access denied. Not your family.'}), 403
    
    completed_chore = CompletedChore(
        chore_id=chore.id,
        child_id=current_user.id
    )
    db.session.add(completed_chore)
    db.session.commit()
    
    activity_logger.log_activity(
        current_user.id,
        'chore_completed',
        {
            'chore_id': chore.id,
            'chore_name': chore.name,
            'completion_id': completed_chore.id
        }
    )
    
    return jsonify({
        'message': 'Chore marked as completed! Waiting for parent verification.',
        'completed_chore_id': completed_chore.id
    })
