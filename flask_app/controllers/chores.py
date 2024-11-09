from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from flask_app import db
from flask_app.models.user import User, ChoreCategory
from flask_app.models.chore import Chore
from flask_app.forms.chores import ChoreForm
from flask_app.utils.decorators import parent_required
from flask_app.utils.logger import get_logger
from datetime import datetime

chores_bp = Blueprint('chores', __name__, url_prefix='/chores')
logger = get_logger()

@chores_bp.route('/')
@login_required
def list_chores():
    try:
        if current_user.is_parent:
            # Parents see all family chores
            chores = Chore.query.filter_by(family_id=current_user.family_id).all()
        else:
            # Children only see their assigned chores
            chores = Chore.query.filter_by(
                family_id=current_user.family_id,
                assigned_to_id=current_user.id
            ).all()
            
        return render_template('chores/list.html', chores=chores)
        
    except Exception as e:
        logger.error("Error listing chores", exc_info=True)
        flash('Error loading chores.', 'danger')
        return redirect(url_for('main.dashboard'))

@chores_bp.route('/create', methods=['GET', 'POST'])
@login_required
@parent_required
def create_chore():
    form = ChoreForm()
    
    if form.validate_on_submit():
        try:
            chore = Chore(
                title=form.title.data,
                description=form.description.data,
                points=form.points.data,
                due_date=form.due_date.data,
                family_id=current_user.family_id,
                created_by_id=current_user.id,
                assigned_to_id=form.assigned_to.data,
                category_id=form.category_id.data if form.category_id.data != 0 else None
            )
            
            db.session.add(chore)
            db.session.commit()
            
            flash('Chore created successfully!', 'success')
            return redirect(url_for('chores.list_chores'))
            
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating chore", exc_info=True)
            flash('Error creating chore.', 'danger')
    
    return render_template('chores/create.html', form=form)

@chores_bp.route('/complete/<int:chore_id>', methods=['POST'])
@login_required
def complete_chore(chore_id):
    chore = Chore.query.get_or_404(chore_id)
    
    if chore.assigned_to_id != current_user.id:
        flash('You are not assigned to this chore.', 'danger')
        return redirect(url_for('chores.list_chores'))
    
    if chore.complete_chore():
        flash('Chore completed successfully!', 'success')
    else:
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
    print(request.form)
    try:
        # Log the incoming request data
        logger.debug("Category creation request received",
                   extra={
                       "form_data": request.form.to_dict(),
                       "user_id": current_user.id,
                       "family_id": current_user.family_id
                   })
        
        name = request.form.get('name')
        color = request.form.get('color', '#6c757d')  # Default gray color
        icon = request.form.get('icon', 'fa-tasks')   # Default tasks icon
        
        logger.debug("Processing category creation",
                    extra={
                        "category_name": name,
                        "color": color,
                        "icon": icon,
                        "family_id": current_user.family_id
                    })
        
        if not name:
            logger.warning("Attempted to create category without name",
                        extra={
                            "user_id": current_user.id,
                            "form_data": request.form.to_dict()
                        })
            return jsonify({'error': 'Category name is required.'}), 400
            
        category = ChoreCategory(
            name=name,
            color=color,
            icon=icon,
            family_id=current_user.family_id,
            created_by_id=current_user.id
        )
        
        db.session.add(category)
        db.session.commit()
        
        logger.info("Chore category created successfully",
                   extra={
                       "category_id": category.id,
                       "category_name": category.name,
                       "family_id": category.family_id
                   })
        
        return jsonify({
            'id': category.id,
            'name': category.name,
            'color': category.color,
            'icon': category.icon
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error("Error creating category",
                    exc_info=True,
                    extra={
                        "user_id": current_user.id,
                        "form_data": request.form.to_dict()
                    })
        return jsonify({'error': 'Error creating category.'}), 500

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