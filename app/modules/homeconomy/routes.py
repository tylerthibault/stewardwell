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
from datetime import datetime
import secrets

def is_parent():
    return current_user.user_type == 'parent'

def is_child():
    return current_user.user_type == 'child'

@bp.route('/')
@login_required
def index():
    if is_parent():
        return redirect(url_for('homeconomy.parent_dashboard'))
    return redirect(url_for('homeconomy.child_dashboard'))

# Parent Routes
@bp.route('/parent/dashboard')
@login_required
def parent_dashboard():
    if not is_parent():
        flash('Access denied. Parents only.', 'error')
        return redirect(url_for('homeconomy.index'))
    
    family = current_user.family
    return render_template('homeconomy/parent/dashboard.html',
                         family=family)

@bp.route('/family/create', methods=['GET', 'POST'])
@login_required
def create_family():
    if not is_parent():
        flash('Access denied. Parents only.', 'error')
        return redirect(url_for('homeconomy.index'))
    
    form = FamilyForm()
    if form.validate_on_submit():
        family = Family(
            name=form.name.data,
            owner_id=current_user.id
        )
        current_user.family = family
        db.session.add(family)
        db.session.commit()
        flash(f'Family {family.name} created successfully!', 'success')
        return redirect(url_for('homeconomy.parent_dashboard'))
    
    return render_template('homeconomy/family/create.html', form=form)

@bp.route('/family/<int:family_id>/add_child', methods=['GET', 'POST'])
@login_required
def add_child(family_id):
    if not is_parent():
        flash('Access denied. Parents only.', 'error')
        return redirect(url_for('homeconomy.index'))
    
    family = Family.query.get_or_404(family_id)
    if family.owner_id != current_user.id:
        flash('Access denied. Not your family.', 'error')
        return redirect(url_for('homeconomy.index'))
    
    form = AddChildForm()
    if form.validate_on_submit():
        child = User(
            username=form.username.data,
            email=form.email.data,
            user_type='child',
            family_id=family.id
        )
        child.set_password(form.password.data)
        db.session.add(child)
        db.session.commit()
        flash(f'Child {child.username} added successfully!', 'success')
        return redirect(url_for('homeconomy.parent_dashboard'))
    
    return render_template('homeconomy/family/add_child.html', form=form, family=family)

# Chore Management Routes
@bp.route('/chores/create', methods=['GET', 'POST'])
@login_required
def create_chore():
    if not is_parent():
        flash('Access denied. Parents only.', 'error')
        return redirect(url_for('homeconomy.index'))
    
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
        flash(f'Chore {chore.name} created successfully!', 'success')
        return redirect(url_for('homeconomy.parent_dashboard'))
    
    return render_template('homeconomy/chores/create.html', form=form)

@bp.route('/chores/<int:chore_id>/verify', methods=['GET', 'POST'])
@login_required
def verify_chore(chore_id):
    if not is_parent():
        flash('Access denied. Parents only.', 'error')
        return redirect(url_for('homeconomy.index'))
    
    completed_chore = CompletedChore.query.get_or_404(chore_id)
    if completed_chore.chore.family_id != current_user.family.id:
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
            flash('Chore verified and rewards distributed!', 'success')
        return redirect(url_for('homeconomy.parent_dashboard'))
    
    return render_template('homeconomy/chores/verify.html', 
                         form=form, completed_chore=completed_chore)

# Reward Management Routes
@bp.route('/rewards/create', methods=['GET', 'POST'])
@login_required
def create_reward():
    if not is_parent():
        flash('Access denied. Parents only.', 'error')
        return redirect(url_for('homeconomy.index'))
    
    form = RewardForm()
    if form.validate_on_submit():
        reward = Reward(
            name=form.name.data,
            description=form.description.data,
            coin_cost=form.coin_cost.data,
            quantity=form.quantity.data,
            family_id=current_user.family.id
        )
        db.session.add(reward)
        db.session.commit()
        flash(f'Reward {reward.name} created successfully!', 'success')
        return redirect(url_for('homeconomy.parent_dashboard'))
    
    return render_template('homeconomy/rewards/create.html', form=form)

@bp.route('/rewards/<int:reward_id>/fulfill', methods=['GET', 'POST'])
@login_required
def fulfill_reward(reward_id):
    if not is_parent():
        flash('Access denied. Parents only.', 'error')
        return redirect(url_for('homeconomy.index'))
    
    claimed_reward = ClaimedReward.query.get_or_404(reward_id)
    if claimed_reward.reward.family_id != current_user.family.id:
        flash('Access denied. Not your family.', 'error')
        return redirect(url_for('homeconomy.index'))
    
    form = FulfillRewardForm()
    if form.validate_on_submit():
        if form.fulfilled.data:
            claimed_reward.fulfilled = True
            claimed_reward.fulfilled_at = datetime.utcnow()
            claimed_reward.fulfilled_by_id = current_user.id
            db.session.commit()
            flash('Reward fulfilled successfully!', 'success')
        return redirect(url_for('homeconomy.parent_dashboard'))
    
    return render_template('homeconomy/rewards/fulfill.html',
                         form=form, claimed_reward=claimed_reward)

# Goal Management Routes
@bp.route('/goals/create', methods=['GET', 'POST'])
@login_required
def create_goal():
    if not is_parent():
        flash('Access denied. Parents only.', 'error')
        return redirect(url_for('homeconomy.index'))
    
    form = GoalForm()
    if form.validate_on_submit():
        goal = Goal(
            name=form.name.data,
            description=form.description.data,
            points_required=form.points_required.data,
            family_id=current_user.family.id
        )
        db.session.add(goal)
        db.session.commit()
        flash(f'Goal {goal.name} created successfully!', 'success')
        return redirect(url_for('homeconomy.parent_dashboard'))
    
    return render_template('homeconomy/goals/create.html', form=form)

# Child Routes
@bp.route('/child/dashboard')
@login_required
def child_dashboard():
    if not is_child():
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
def complete_chore(chore_id):
    if not is_child():
        return jsonify({'error': 'Access denied. Children only.'}), 403
    
    chore = Chore.query.get_or_404(chore_id)
    if chore.family_id != current_user.family_id:
        return jsonify({'error': 'Access denied. Not your family.'}), 403
    
    completed_chore = CompletedChore(
        chore_id=chore.id,
        child_id=current_user.id
    )
    db.session.add(completed_chore)
    db.session.commit()
    
    return jsonify({
        'message': 'Chore marked as completed! Waiting for parent verification.',
        'completed_chore_id': completed_chore.id
    })

@bp.route('/rewards/<int:reward_id>/claim', methods=['POST'])
@login_required
def claim_reward(reward_id):
    if not is_child():
        return jsonify({'error': 'Access denied. Children only.'}), 403
    
    reward = Reward.query.get_or_404(reward_id)
    if reward.family_id != current_user.family_id:
        return jsonify({'error': 'Access denied. Not your family.'}), 403
    
    if current_user.coins < reward.coin_cost:
        return jsonify({'error': 'Not enough coins!'}), 400
    
    if reward.quantity == 0:
        return jsonify({'error': 'Reward out of stock!'}), 400
    
    current_user.coins -= reward.coin_cost
    if reward.quantity > 0:
        reward.quantity -= 1
    
    claimed_reward = ClaimedReward(
        reward_id=reward.id,
        child_id=current_user.id
    )
    db.session.add(claimed_reward)
    db.session.commit()
    
    return jsonify({
        'message': 'Reward claimed successfully!',
        'new_coin_balance': current_user.coins
    })
