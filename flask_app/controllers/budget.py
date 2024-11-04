from flask_app import app, db
from flask import render_template, redirect, session, request, flash, jsonify
from flask_app.config.helper import login_required
from flask_app.models.users import User
from flask_app.models.families import Family
from flask_app.models.budgets import Budget
from flask_app.models.budget_categories import BudgetCategory
from flask_app.models.transactions import BudgetTransaction
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

@app.route('/family/<int:family_id>/budget')
@login_required
def family_budgets(family_id):
    user = User.get(session_token=session['session_token'])
    family = Family.get(id=family_id)
    
    if not family or not any(m.family_id == family_id for m in user.family_memberships):
        flash("Access denied", "danger")
        return redirect('/dashboard')
    
    context = {
        'user': user,
        'family': family,
        'budgets': family.budgets
    }
    return render_template('inside/budget/list.html', **context)

@app.route('/family/<int:family_id>/budget/create', methods=['GET', 'POST'])
@login_required
def create_budget(family_id):
    user = User.get(session_token=session['session_token'])
    family = Family.get(id=family_id)
    
    if not family or not user.is_parent_in_family(family_id):
        flash("Access denied", "danger")
        return redirect('/dashboard')
    
    if request.method == 'GET':
        return render_template('inside/budget/create.html', user=user, family=family)
    
    # Create the budget
    budget = Budget.create(
        family_id=family_id,
        name=request.form['name'],
        description=request.form.get('description', '')
    )
    
    if not budget:
        return redirect(f'/family/{family_id}/budget/create')

    # Create categories
    categories_data = []
    i = 0
    while f'categories[{i}][name]' in request.form:
        categories_data.append({
            'name': request.form[f'categories[{i}][name]'],
            'planned_amount': float(request.form[f'categories[{i}][planned_amount]']),
            'budget_id': budget.id
        })
        i += 1

    # Add categories to the budget
    for category_data in categories_data:
        category = BudgetCategory(**category_data)
        db.session.add(category)
    
    try:
        db.session.commit()
        flash("Budget created successfully!", "success")
        return redirect(f'/family/{family_id}/budget/{budget.id}')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash("Error creating budget categories: " + str(e), "danger")
        return redirect(f'/family/{family_id}/budget/create')

@app.route('/family/<int:family_id>/budget/<int:budget_id>')
@login_required
def view_budget(family_id, budget_id):
    user = User.get(session_token=session['session_token'])
    budget = Budget.get(id=budget_id, family_id=family_id)
    
    if not budget or not any(m.family_id == family_id for m in user.family_memberships):
        flash("Access denied", "danger")
        return redirect('/dashboard')
    
    context = {
        'user': user,
        'budget': budget,
        'categories': budget.categories,
        'transactions': budget.transactions
    }
    return render_template('inside/budget/view.html', **context) 

@app.route('/family/<int:family_id>/budget/<int:budget_id>/transaction', methods=['POST'])
@login_required
def add_transaction(family_id, budget_id):
    user = User.get(session_token=session['session_token'])
    budget = Budget.get(id=budget_id, family_id=family_id)
    
    if not budget or not any(m.family_id == family_id for m in user.family_memberships):
        flash("Access denied", "danger")
        return redirect('/dashboard')
    
    try:
        # Create the transaction
        transaction = BudgetTransaction.create(
            budget_id=budget_id,
            category_id=request.form['category_id'],
            user_id=user.id,
            description=request.form['description'],
            amount=float(request.form['amount']),
            date=datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        )
        
        if transaction:
            flash("Transaction added successfully!", "success")
        
    except (ValueError, KeyError) as e:
        flash("Invalid transaction data: " + str(e), "danger")
    except SQLAlchemyError as e:
        flash("Error adding transaction: " + str(e), "danger")
    
    return redirect(f'/family/{family_id}/budget/{budget_id}')

@app.route('/family/<int:family_id>/budget/<int:budget_id>/transaction/<int:transaction_id>', methods=['DELETE'])
@login_required
def delete_transaction(family_id, budget_id, transaction_id):
    user = User.get(session_token=session['session_token'])
    transaction = BudgetTransaction.query.get(transaction_id)
    
    if not transaction or transaction.user_id != user.id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        budget = transaction.budget
        db.session.delete(transaction)
        db.session.commit()
        
        # Recalculate budget total
        budget.calculate_total()
        
        return jsonify({'success': True})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/family/<int:family_id>/budget/<int:budget_id>/category', methods=['POST'])
@login_required
def add_category(family_id, budget_id):
    user = User.get(session_token=session['session_token'])
    budget = Budget.get(id=budget_id, family_id=family_id)
    
    if not budget or not user.is_parent_in_family(family_id):
        flash("Access denied", "danger")
        return redirect('/dashboard')
    
    try:
        category = BudgetCategory.create(
            budget_id=budget_id,
            name=request.form['name'],
            planned_amount=float(request.form['planned_amount'])
        )
        
        if category:
            flash("Category added successfully!", "success")
        
    except (ValueError, KeyError) as e:
        flash("Invalid category data: " + str(e), "danger")
    except SQLAlchemyError as e:
        flash("Error adding category: " + str(e), "danger")
    
    return redirect(f'/family/{family_id}/budget/{budget_id}')

@app.route('/family/<int:family_id>/budget/<int:budget_id>/transaction/<int:transaction_id>/move', methods=['POST'])
@login_required
def move_transaction(family_id, budget_id, transaction_id):
    user = User.get(session_token=session['session_token'])
    transaction = BudgetTransaction.query.get(transaction_id)
    
    if not transaction or transaction.user_id != user.id:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        new_category_id = data.get('new_category_id')
        
        # Verify the new category belongs to the same budget
        new_category = BudgetCategory.query.get(new_category_id)
        if not new_category or new_category.budget_id != budget_id:
            return jsonify({'success': False, 'message': 'Invalid category'}), 400
        
        # Move the transaction
        transaction.category_id = new_category_id
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Transaction moved successfully'
        })
        
    except (ValueError, KeyError) as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500