from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app.models.user import User, Chore, ChoreCategory
from app import db
from datetime import datetime, timedelta
from functools import wraps
import logging

logger = logging.getLogger(__name__)

chores_bp = Blueprint('chores', __name__, url_prefix='/chores')

def parent_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_parent:
            flash('You need to be a parent to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@chores_bp.route('/')
@login_required
def list_chores():
    if current_user.is_parent:
        # Parents see all family chores
        chores = Chore.query.filter_by(family_id=current_user.family_id).all()
    else:
        # Children only see their assigned chores
        chores = Chore.query.filter_by(
            family_id=current_user.family_id,
            assigned_to_id=current_user.id
        ).all()
    
    # Group chores by status
    pending_chores = [c for c in chores if c.status == 'pending']
    completed_chores = [c for c in chores if c.status == 'completed']
    overdue_chores = [c for c in chores if c.status == 'overdue']
    
    # Get categories for the form
    categories = ChoreCategory.query.filter_by(family_id=current_user.family_id).all()
    
    return render_template('chores/list.html',
                         pending_chores=pending_chores,
                         completed_chores=completed_chores,
                         overdue_chores=overdue_chores,
                         categories=categories)

@chores_bp.route('/create', methods=['GET', 'POST'])
@login_required
@parent_required
def create_chore():
    try:
        form = ChoreForm()
        if form.validate_on_submit():
            chore = Chore(
                title=form.title.data,
                description=form.description.data,
                points=form.points.data,
                due_date=form.due_date.data,
                family_id=current_user.family_id,
                created_by_id=current_user.id,
                assigned_to_id=form.assigned_to.data,
                category_id=form.category.data
            )
            
            db.session.add(chore)
            db.session.commit()
            
            logger.info("New chore created",
                       extra={
                           "chore_id": chore.id,
                           "title": chore.title,
                           "assigned_to": chore.assigned_to_id,
                           "created_by": current_user.id,
                           "family_id": current_user.family_id
                       })
            
            flash('Chore created successfully!', 'success')
            return redirect(url_for('chores.list_chores'))
            
    except Exception as e:
        db.session.rollback()
        logger.error("Error creating chore",
                    exc_info=True,
                    extra={
                        "form_data": request.form,
                        "user_id": current_user.id
                    })
        flash('Error creating chore.', 'danger')
    
    return render_template('chores/create.html', form=form)

@chores_bp.route('/<int:chore_id>/complete', methods=['POST'])
@login_required
def complete_chore(chore_id):
    chore = Chore.query.get_or_404(chore_id)
    
    # Verify the chore belongs to the user's family
    if chore.family_id != current_user.family_id:
        flash('Invalid chore.', 'danger')
        return redirect(url_for('chores.list_chores'))
    
    # Verify the chore is assigned to the current user (if not a parent)
    if not current_user.is_parent and chore.assigned_to_id != current_user.id:
        flash('This chore is not assigned to you.', 'danger')
        return redirect(url_for('chores.list_chores'))
    
    try:
        chore.status = 'completed'
        chore.completed_at = datetime.utcnow()
        
        # Award coins to the assigned user
        if chore.assigned_to:
            chore.assigned_to.coins += chore.coins
            
        # Award points to the family
        for member in chore.assigned_to.family.members:
            member.family_points += chore.points
        
        db.session.commit()
        flash(f'Chore completed! Earned {chore.coins} coins and {chore.points} family points!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error completing chore.', 'danger')
    
    return redirect(url_for('chores.list_chores'))

@chores_bp.route('/categories')
@login_required
@parent_required
def list_categories():
    categories = ChoreCategory.query.filter_by(family_id=current_user.family_id).all()
    return render_template('chores/categories.html', categories=categories)

@chores_bp.route('/categories/create', methods=['POST'])
@login_required
@parent_required
def create_category():
    if request.is_json:
        data = request.get_json()
        name = data.get('name')
        color = data.get('color', '#6c757d')
        icon = data.get('icon', 'fa-list')
    else:
        name = request.form.get('name')
        color = request.form.get('color', '#6c757d')
        icon = request.form.get('icon', 'fa-list')
    
    if not name:
        if request.is_json:
            return jsonify({'error': 'Category name is required.'}), 400
        flash('Category name is required.', 'danger')
        return redirect(url_for('chores.list_chores'))
    
    try:
        category = ChoreCategory(
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
    
    return redirect(url_for('chores.list_chores'))

@chores_bp.route('/categories/<int:category_id>/edit', methods=['POST'])
@login_required
@parent_required
def edit_category(category_id):
    category = ChoreCategory.query.get_or_404(category_id)
    
    # Verify the category belongs to the user's family
    if category.family_id != current_user.family_id:
        flash('Invalid category.', 'danger')
        return redirect(url_for('chores.list_categories'))
    
    name = request.form.get('name')
    color = request.form.get('color')
    icon = request.form.get('icon')
    
    if not name:
        flash('Category name is required.', 'danger')
        return redirect(url_for('chores.list_categories'))
    
    try:
        category.name = name
        category.color = color
        category.icon = icon
        
        db.session.commit()
        flash('Category updated successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error updating category.', 'danger')
    
    return redirect(url_for('chores.list_categories'))

@chores_bp.route('/categories/<int:category_id>/delete', methods=['POST'])
@login_required
@parent_required
def delete_category(category_id):
    category = ChoreCategory.query.get_or_404(category_id)
    
    # Verify the category belongs to the user's family
    if category.family_id != current_user.family_id:
        flash('Invalid category.', 'danger')
        return redirect(url_for('chores.list_categories'))
    
    try:
        # Remove category from chores but don't delete the chores
        Chore.query.filter_by(category_id=category.id).update({Chore.category_id: None})
        
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error deleting category.', 'danger')
    
    return redirect(url_for('chores.list_categories'))

@chores_bp.route('/<int:chore_id>/edit', methods=['POST'])
@login_required
@parent_required
def edit_chore(chore_id):
    chore = Chore.query.get_or_404(chore_id)
    
    # Verify the chore belongs to the user's family
    if chore.family_id != current_user.family_id:
        flash('Invalid chore.', 'danger')
        return redirect(url_for('chores.list_chores'))
    
    title = request.form.get('title')
    description = request.form.get('description')
    coins = request.form.get('coins', type=int)
    points = request.form.get('points', type=int)
    frequency = request.form.get('frequency')
    assigned_to_id = request.form.get('assigned_to_id', type=int)
    category_id = request.form.get('category_id')
    has_due_date = request.form.get('has_due_date')
    due_date_str = request.form.get('due_date')
    
    if not all([title, coins, points, frequency, assigned_to_id]):
        flash('Please provide all required fields.', 'danger')
        return redirect(url_for('chores.list_chores'))
    
    try:
        chore.title = title
        chore.description = description
        chore.coins = coins
        chore.points = points
        chore.frequency = frequency
        chore.assigned_to_id = assigned_to_id
        chore.category_id = category_id if category_id else None
        
        # Update due date
        if has_due_date and due_date_str:
            chore.due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
        else:
            chore.due_date = None
        
        db.session.commit()
        flash('Chore updated successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error updating chore.', 'danger')
    
    return redirect(url_for('chores.list_chores'))

@chores_bp.route('/clone/<int:chore_id>', methods=['POST'])
@login_required
def clone_chore(chore_id):
    if not current_user.is_parent:
        flash('Only parents can clone chores.', 'error')
        return redirect(url_for('chores.list_chores'))
    
    chore = Chore.query.filter_by(id=chore_id, family_id=current_user.family_id).first_or_404()
    assigned_to_id = request.form.get('assigned_to_id')
    
    if not assigned_to_id:
        flash('Please select a child to assign the chore to.', 'error')
        return redirect(url_for('chores.list_chores'))
    
    # Create new chore with same details but different assigned_to_id
    new_chore = Chore(
        title=chore.title,
        description=chore.description,
        category_id=chore.category_id,
        coins=chore.coins,
        points=chore.points,
        frequency=chore.frequency,
        family_id=chore.family_id,
        created_by_id=current_user.id,
        assigned_to_id=assigned_to_id,
        due_date=chore.due_date
    )
    
    try:
        db.session.add(new_chore)
        db.session.commit()
        flash('Chore cloned successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error cloning chore. Please try again.', 'error')
        
    return redirect(url_for('chores.list_chores'))