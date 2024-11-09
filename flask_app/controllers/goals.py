from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app.models.user import User, Goal, GoalCategory
from app import db
from datetime import datetime
from functools import wraps

goals_bp = Blueprint('goals', __name__, url_prefix='/goals')

def parent_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_parent:
            flash('You need to be a parent to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@goals_bp.route('/')
@login_required
def list_goals():
    if not current_user.family:
        flash('You need to be part of a family to view goals.', 'warning')
        return redirect(url_for('main.dashboard'))
    
    categories = GoalCategory.query.filter_by(family_id=current_user.family_id).all()
    
    active_goals = Goal.query.filter_by(
        family_id=current_user.family_id,
        is_completed=False
    ).order_by(Goal.created_at.desc()).all()
    
    completed_goals = Goal.query.filter_by(
        family_id=current_user.family_id,
        is_completed=True
    ).order_by(Goal.completed_at.desc()).all()
    
    # Calculate total family points
    family_points = sum(member.family_points for member in current_user.family.members)
    
    return render_template('goals/list.html',
                         active_goals=active_goals,
                         completed_goals=completed_goals,
                         family_points=family_points,
                         categories=categories)

@goals_bp.route('/create', methods=['POST'])
@login_required
@parent_required
def create_goal():
    title = request.form.get('title')
    description = request.form.get('description')
    points_required = request.form.get('points_required', type=int)
    category_id = request.form.get('category_id')
    
    if not all([title, points_required]):
        flash('Please provide all required fields.', 'danger')
        return redirect(url_for('goals.list_goals'))
    
    try:
        goal = Goal(
            title=title,
            description=description,
            points_required=points_required,
            category_id=category_id if category_id else None,
            family_id=current_user.family_id,
            created_by_id=current_user.id
        )
        
        db.session.add(goal)
        db.session.commit()
        flash('Goal created successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error creating goal.', 'danger')
        print(f"Error: {str(e)}")
    
    return redirect(url_for('goals.list_goals'))

@goals_bp.route('/<int:goal_id>/complete', methods=['POST'])
@login_required
@parent_required
def complete_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    
    # Verify the goal belongs to the user's family
    if goal.family_id != current_user.family_id:
        flash('Invalid goal.', 'danger')
        return redirect(url_for('goals.list_goals'))
    
    # Calculate total family points
    family_points = sum(member.family_points for member in current_user.family.members)
    
    if family_points < goal.points_required:
        flash('Not enough family points to complete this goal.', 'warning')
        return redirect(url_for('goals.list_goals'))
    
    try:
        # Mark goal as completed
        goal.is_completed = True
        goal.completed_at = datetime.utcnow()
        
        # Deduct points from family members
        points_per_member = goal.points_required // len(current_user.family.members)
        remainder = goal.points_required % len(current_user.family.members)
        
        for i, member in enumerate(current_user.family.members):
            # Add remainder to first member's deduction
            deduction = points_per_member + (remainder if i == 0 else 0)
            member.family_points -= deduction
        
        db.session.commit()
        flash('Family goal completed successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error completing family goal.', 'danger')
    
    return redirect(url_for('goals.list_goals'))

@goals_bp.route('/<int:goal_id>/delete', methods=['POST'])
@login_required
@parent_required
def delete_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    
    # Verify the goal belongs to the user's family
    if goal.family_id != current_user.family_id:
        flash('Invalid goal.', 'danger')
        return redirect(url_for('goals.list_goals'))
    
    try:
        db.session.delete(goal)
        db.session.commit()
        flash('Family goal deleted successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error deleting family goal.', 'danger')
    
    return redirect(url_for('goals.list_goals'))

@goals_bp.route('/categories/create', methods=['POST'])
@login_required
@parent_required
def create_category():
    if request.is_json:
        data = request.get_json()
        name = data.get('name')
        color = data.get('color', '#6c757d')
        icon = data.get('icon', 'fa-star')
    else:
        name = request.form.get('name')
        color = request.form.get('color', '#6c757d')
        icon = request.form.get('icon', 'fa-star')
    
    if not name:
        if request.is_json:
            return jsonify({'error': 'Category name is required.'}), 400
        flash('Category name is required.', 'danger')
        return redirect(url_for('goals.list_goals'))
    
    try:
        category = GoalCategory(
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
    
    return redirect(url_for('goals.list_goals')) 