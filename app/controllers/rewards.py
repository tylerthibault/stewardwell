from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app.models.user import User, Reward, RewardRedemption, RewardCategory
from app import db
from datetime import datetime
from functools import wraps

rewards_bp = Blueprint('rewards', __name__, url_prefix='/rewards')

def parent_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_parent:
            flash('You need to be a parent to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@rewards_bp.route('/')
@login_required
def list_rewards():
    if current_user.is_parent:
        # Parents see all rewards and redemptions
        rewards = Reward.query.filter_by(family_id=current_user.family_id).all()
        pending_redemptions = RewardRedemption.query.filter_by(
            status='pending'
        ).join(Reward).filter(
            Reward.family_id == current_user.family_id
        ).all()
    else:
        # Children see available rewards and their redemptions
        rewards = Reward.query.filter_by(
            family_id=current_user.family_id,
            is_available=True
        ).all()
        pending_redemptions = RewardRedemption.query.filter_by(
            user_id=current_user.id
        ).order_by(RewardRedemption.redeemed_at.desc()).all()
    
    # Get categories and sort them by name
    categories = RewardCategory.query.filter_by(
        family_id=current_user.family_id
    ).order_by(RewardCategory.name).all()
    
    return render_template('rewards/list.html',
                         rewards=rewards,
                         pending_redemptions=pending_redemptions,
                         categories=categories,
                         user_coins=current_user.coins)

@rewards_bp.route('/create', methods=['POST'])
@login_required
@parent_required
def create_reward():
    title = request.form.get('title')
    description = request.form.get('description')
    cost = request.form.get('cost', type=int)
    
    if not all([title, cost]):
        flash('Please provide all required fields.', 'danger')
        return redirect(url_for('rewards.list_rewards'))
    
    try:
        reward = Reward(
            title=title,
            description=description,
            cost=cost,
            family_id=current_user.family_id,
            created_by_id=current_user.id
        )
        
        db.session.add(reward)
        db.session.commit()
        flash('Reward created successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error creating reward.', 'danger')
    
    return redirect(url_for('rewards.list_rewards'))

@rewards_bp.route('/<int:reward_id>/redeem', methods=['POST'])
@login_required
def redeem_reward(reward_id):
    if current_user.is_parent:
        flash('Parents cannot redeem rewards.', 'danger')
        return redirect(url_for('rewards.list_rewards'))
    
    reward = Reward.query.get_or_404(reward_id)
    
    # Verify the reward belongs to the user's family
    if reward.family_id != current_user.family_id:
        flash('Invalid reward.', 'danger')
        return redirect(url_for('rewards.list_rewards'))
    
    # Check if reward is available
    if not reward.is_available:
        flash('This reward is not currently available.', 'danger')
        return redirect(url_for('rewards.list_rewards'))
    
    # Check if user has enough coins
    if current_user.coins < reward.cost:
        flash('You do not have enough coins for this reward.', 'danger')
        return redirect(url_for('rewards.list_rewards'))
    
    try:
        # Create redemption request
        redemption = RewardRedemption(
            reward_id=reward.id,
            user_id=current_user.id,
            cost=reward.cost  # Store current cost
        )
        
        # Deduct coins immediately (can be refunded if denied)
        current_user.coins -= reward.cost
        
        db.session.add(redemption)
        db.session.commit()
        flash('Reward redemption requested!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error redeeming reward.', 'danger')
    
    return redirect(url_for('rewards.list_rewards'))

@rewards_bp.route('/redemption/<int:redemption_id>/<string:action>', methods=['POST'])
@login_required
@parent_required
def handle_redemption(redemption_id, action):
    redemption = RewardRedemption.query.get_or_404(redemption_id)
    
    # Verify the redemption belongs to the user's family
    if redemption.reward.family_id != current_user.family_id:
        flash('Invalid redemption request.', 'danger')
        return redirect(url_for('rewards.list_rewards'))
    
    try:
        if action == 'approve':
            redemption.status = 'approved'
            flash('Redemption approved!', 'success')
            
        elif action == 'deny':
            redemption.status = 'denied'
            # Refund the coins
            redemption.user.coins += redemption.cost
            flash('Redemption denied and coins refunded.', 'info')
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        flash('Error processing redemption.', 'danger')
    
    return redirect(url_for('rewards.list_rewards'))

@rewards_bp.route('/<int:reward_id>/toggle', methods=['POST'])
@login_required
@parent_required
def toggle_reward(reward_id):
    reward = Reward.query.get_or_404(reward_id)
    
    # Verify the reward belongs to the user's family
    if reward.family_id != current_user.family_id:
        flash('Invalid reward.', 'danger')
        return redirect(url_for('rewards.list_rewards'))
    
    try:
        reward.is_available = not reward.is_available
        db.session.commit()
        status = "available" if reward.is_available else "unavailable"
        flash(f'Reward is now {status}.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error updating reward.', 'danger')
    
    return redirect(url_for('rewards.list_rewards'))

@rewards_bp.route('/<int:reward_id>/edit', methods=['POST'])
@login_required
@parent_required
def edit_reward(reward_id):
    reward = Reward.query.get_or_404(reward_id)
    
    # Verify the reward belongs to the user's family
    if reward.family_id != current_user.family_id:
        flash('Invalid reward.', 'danger')
        return redirect(url_for('rewards.list_rewards'))
    
    title = request.form.get('title')
    description = request.form.get('description')
    cost = request.form.get('cost', type=int)
    category_id = request.form.get('category_id')
    
    if not all([title, cost]):
        flash('Please provide all required fields.', 'danger')
        return redirect(url_for('rewards.list_rewards'))
    
    try:
        reward.title = title
        reward.description = description
        reward.cost = cost
        reward.category_id = category_id if category_id else None
        
        db.session.commit()
        flash('Reward updated successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error updating reward.', 'danger')
    
    return redirect(url_for('rewards.list_rewards'))

@rewards_bp.route('/categories')
@login_required
@parent_required
def list_categories():
    categories = RewardCategory.query.filter_by(family_id=current_user.family_id).all()
    return render_template('rewards/categories.html', categories=categories)

@rewards_bp.route('/categories/create', methods=['POST'])
@login_required
@parent_required
def create_category():
    if request.is_json:
        data = request.get_json()
        name = data.get('name')
        color = data.get('color', '#6c757d')
        icon = data.get('icon', 'fa-gift')
    else:
        name = request.form.get('name')
        color = request.form.get('color', '#6c757d')
        icon = request.form.get('icon', 'fa-gift')
    
    if not name:
        if request.is_json:
            return jsonify({'error': 'Category name is required.'}), 400
        flash('Category name is required.', 'danger')
        return redirect(url_for('rewards.list_rewards'))
    
    try:
        category = RewardCategory(
            name=name,
            color=color,
            icon=icon,
            family_id=current_user.family_id,
            created_by_id=current_user.id
        )
        
        db.session.add(category)
        db.session.commit()
        
        if request.is_json:
            return jsonify({
                'message': 'Category created successfully!',
                'category_id': category.id
            })
            
        flash('Category created successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'error': 'Error creating category.'}), 500
        flash('Error creating category.', 'danger')
    
    return redirect(url_for('rewards.list_rewards'))

@rewards_bp.route('/categories/<int:category_id>/edit', methods=['POST'])
@login_required
@parent_required
def edit_category(category_id):
    category = RewardCategory.query.get_or_404(category_id)
    
    # Verify the category belongs to the user's family
    if category.family_id != current_user.family_id:
        flash('Invalid category.', 'danger')
        return redirect(url_for('rewards.list_categories'))
    
    name = request.form.get('name')
    color = request.form.get('color')
    icon = request.form.get('icon')
    
    if not name:
        flash('Category name is required.', 'danger')
        return redirect(url_for('rewards.list_categories'))
    
    try:
        category.name = name
        category.color = color
        category.icon = icon
        
        db.session.commit()
        flash('Category updated successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error updating category.', 'danger')
    
    return redirect(url_for('rewards.list_categories'))

@rewards_bp.route('/categories/<int:category_id>/delete', methods=['POST'])
@login_required
@parent_required
def delete_category(category_id):
    category = RewardCategory.query.get_or_404(category_id)
    
    # Verify the category belongs to the user's family
    if category.family_id != current_user.family_id:
        flash('Invalid category.', 'danger')
        return redirect(url_for('rewards.list_categories'))
    
    try:
        # Remove category from rewards but don't delete the rewards
        Reward.query.filter_by(category_id=category.id).update({Reward.category_id: None})
        
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error deleting category.', 'danger')
    
    return redirect(url_for('rewards.list_categories')) 