from flask_app import app, db
from flask import render_template, redirect, session, request, flash, jsonify, url_for
from flask_app.config.helper import login_required, kid_required, parent_required
from flask_app.models.users import User
from flask_app.models.families import Family
from flask_app.models.chores import Chore
from flask_app.models.chore_assignments import ChoreAssignment
from flask_app.models.rewards import Reward
from flask_app.models.reward_redemptions import RewardRedemption
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

def serialize_reward(reward):
    """Convert a Reward object to a dictionary for JSON serialization"""
    return {
        'id': reward.id,
        'name': reward.name,
        'description': reward.description,
        'coin_cost': reward.coin_cost,
        'points_required': reward.points_required,
        'is_family_reward': reward.is_family_reward,
        'available': reward.available,
        'family_id': reward.family_id
    }

@app.route('/family/<int:family_id>/chores')
@parent_required
def family_chores(family_id):
    user = User.get(session_token=session['session_token'])
    family = Family.get(id=family_id)
    
    if not family or not any(m.family_id == family_id for m in user.family_memberships):
        flash("Access denied", "danger")
        return redirect('/dashboard')
    
    # Get chores with no active assignments
    unassigned_chores = [chore for chore in family.chores 
                        if not any(assignment.status == 'pending' 
                                 for assignment in chore.assignments)]
    
    context = {
        'user': user,
        'family': family,
        'chores': family.chores,
        'unassigned_chores': unassigned_chores,
        'pending_assignments': [a for a in user.chores_assigned if a.status == 'pending'],
        'completed_assignments': [a for a in user.chores_assigned if a.status == 'completed'],
        'approved_assignments': [a for a in user.chores_assigned if a.status == 'approved']
    }
    return render_template('inside/chores/dashboard.html', **context)

@app.route('/family/<int:family_id>/chores/create', methods=['GET', 'POST'])
@login_required
def create_chore(family_id):
    user = User.get(session_token=session['session_token'])
    family = Family.get(id=family_id)
    
    if not family or not user.is_parent_in_family(family_id):
        flash("Access denied", "danger")
        return redirect('/dashboard')
    
    if request.method == 'GET':
        return render_template('inside/chores/create.html', user=user, family=family)
    
    try:
        chore = Chore.create(
            family_id=family_id,
            name=request.form['name'],
            description=request.form.get('description', ''),
            coin_value=int(request.form['coin_value']),
            family_points=int(request.form['family_points']),
            recurring=bool(request.form.get('recurring', False)),
            recurring_frequency=request.form.get('recurring_frequency')
        )
        
        if chore:
            flash("Chore created successfully!", "success")
            return redirect(f'/family/{family_id}/chores')
            
    except (ValueError, KeyError) as e:
        flash("Invalid chore data: " + str(e), "danger")
    except SQLAlchemyError as e:
        flash("Error creating chore: " + str(e), "danger")
    
    return redirect(f'/family/{family_id}/chores/create')

@app.route('/family/<int:family_id>/chores/<int:chore_id>/assign', methods=['POST'])
@login_required
def assign_chore(family_id, chore_id):
    user = User.get(session_token=session['session_token'])
    family = Family.get(id=family_id)
    
    if not family or not user.is_parent_in_family(family_id):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        assignment = ChoreAssignment.create(
            chore_id=chore_id,
            assigned_to_id=request.form['assigned_to_id'],
            assigned_by_id=user.id
        )
        
        if assignment:
            flash("Chore assigned successfully!", "success")
            return redirect(f'/family/{family_id}/chores')
            
    except SQLAlchemyError as e:
        flash("Error assigning chore: " + str(e), "danger")
    
    return redirect(f'/family/{family_id}/chores')

@app.route('/family/<int:family_id>/chores/assignment/<int:assignment_id>/complete', methods=['POST'])
@login_required
def complete_chore(family_id, assignment_id):
    user = User.get(session_token=session['session_token'])
    assignment = ChoreAssignment.query.get(assignment_id)
    
    # Check if user is either the assigned child or a parent viewing as child
    is_assigned_child = assignment and assignment.assigned_to_id == user.id
    is_parent_viewing_child = (session.get('viewing_as_child') and 
                             assignment and 
                             assignment.assigned_to_id == session['viewing_as_child']['id'])
    
    if not assignment or (not is_assigned_child and not is_parent_viewing_child):
        return jsonify({
            'success': False, 
            'message': 'Access denied'
        }), 403
    
    try:
        assignment.complete()
        return jsonify({
            'success': True,
            'message': 'Chore completed successfully!'
        })
    except SQLAlchemyError as e:
        return jsonify({
            'success': False, 
            'message': str(e)
        }), 500

@app.route('/family/<int:family_id>/chores/assignment/<int:assignment_id>/approve', methods=['POST'])
@login_required
def approve_chore(family_id, assignment_id):
    user = User.get(session_token=session['session_token'])
    assignment = ChoreAssignment.query.get(assignment_id)
    
    if not assignment or not user.is_parent_in_family(family_id):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        assignment.approve()
        return jsonify({'success': True})
    except SQLAlchemyError as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/family/<int:family_id>/store')
@parent_required
def personal_store(family_id):
    user = User.get(session_token=session['session_token'])
    family = Family.get(id=family_id)
    
    if not family or not any(m.family_id == family_id for m in user.family_memberships):
        flash("Access denied", "danger")
        return redirect('/dashboard')
    
    personal_rewards = [r for r in family.rewards if not r.is_family_reward]
    
    context = {
        'user': user,
        'family': family,
        'rewards': personal_rewards
    }
    return render_template('inside/chores/personal_store.html', **context)

@app.route('/family/<int:family_id>/family-store')
@parent_required
def family_store(family_id):
    user = User.get(session_token=session['session_token'])
    family = Family.get(id=family_id)
    
    if not family or not any(m.family_id == family_id for m in user.family_memberships):
        flash("Access denied", "danger")
        return redirect('/dashboard')
    
    family_rewards = [r for r in family.rewards if r.is_family_reward]
    
    context = {
        'user': user,
        'family': family,
        'rewards': family_rewards
    }
    return render_template('inside/chores/family_store.html', **context)

@app.route('/family/<int:family_id>/rewards/manage', methods=['GET', 'POST'])
@parent_required
def manage_rewards(family_id):
    """Manage rewards as a parent"""
    user = User.get(session_token=session['session_token'])
    family = Family.get(id=family_id)
    
    if not family or not user.is_parent_in_family(family_id):
        flash("Access denied", "danger")
        return redirect('/dashboard')
    
    if request.method == 'POST':
        try:
            # Get form data with defaults for numeric fields
            coin_cost = request.form.get('coin_cost', '0')
            points_required = request.form.get('points_required', '0')
            
            # Convert empty strings to 0
            coin_cost = int(coin_cost) if coin_cost.strip() else 0
            points_required = int(points_required) if points_required.strip() else 0
            
            # Create new reward
            reward = Reward.create(
                family_id=family_id,
                name=request.form['name'],
                description=request.form.get('description', ''),
                coin_cost=coin_cost,
                points_required=points_required,
                is_family_reward=request.form.get('is_family_reward') == 'true',
                available=True
            )
            
            if reward:
                flash("Reward created successfully!", "success")
                return jsonify({'success': True})
            return jsonify({'success': False, 'message': 'Error creating reward'}), 500
            
        except (ValueError, KeyError) as e:
            return jsonify({'success': False, 'message': f'Please enter valid numbers for costs and points'}), 400
        except SQLAlchemyError as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    # Get rewards for both individual and family categories
    individual_rewards = [r for r in family.rewards if not r.is_family_reward]
    family_rewards = [r for r in family.rewards if r.is_family_reward]
    
    # Serialize rewards for JSON
    serialized_rewards = [serialize_reward(r) for r in family.rewards]
    
    context = {
        'user': user,
        'family': family,
        'individual_rewards': individual_rewards,
        'family_rewards': family_rewards,
        'rewards': serialized_rewards  # Pass serialized rewards to template
    }
    return render_template('inside/chores/manage_rewards.html', **context)

@app.route('/family/<int:family_id>/switch-view')
@login_required
def switch_child_view(family_id):
    user = User.get(session_token=session['session_token'])
    child_id = request.args.get('child_id')
    
    if not user.is_parent_in_family(family_id):
        flash("Access denied", "danger")
        return redirect(f'/family/{family_id}/chores')
    
    if not child_id:
        # Switch back to parent view - clear all child-related session data
        session_keys_to_remove = ['child_view', 'viewing_as_child']
        for key in session_keys_to_remove:
            if key in session:
                del session[key]
        flash("Switched to parent view", "info")
        return redirect(f'/family/{family_id}/chores')
    
    # Switch to child view
    child = User.query.get(child_id)
    if not child or not any(m.user_id == child.id and m.family_id == family_id 
                          and m.role == 'child' for m in child.family_memberships):
        flash("Invalid child selected", "danger")
        return redirect(f'/family/{family_id}/chores')
    
    # Store both the child's ID and their family for the view
    session['viewing_as_child'] = {
        'id': child.id,
        'family_id': family_id
    }
    flash(f"Viewing as {child.first_name}", "info")
    
    # Redirect to kid dashboard instead of family chores
    return redirect(url_for('kid_dashboard'))

@app.route('/family/<int:family_id>/chores/<int:chore_id>/clone', methods=['POST'])
@login_required
def clone_chore(family_id, chore_id):
    user = User.get(session_token=session['session_token'])
    family = Family.get(id=family_id)
    
    if not family or not user.is_parent_in_family(family_id):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    # Get the original chore
    original_chore = Chore.query.get(chore_id)
    if not original_chore or original_chore.family_id != family_id:
        return jsonify({'success': False, 'message': 'Chore not found'}), 404
    
    try:
        # Get the target child ID from the request
        assigned_to_id = request.json.get('assigned_to_id')
        if not assigned_to_id:
            return jsonify({'success': False, 'message': 'No target child specified'}), 400
            
        # Create a new chore assignment with the same details
        assignment = ChoreAssignment.create(
            chore_id=chore_id,
            assigned_to_id=assigned_to_id,
            assigned_by_id=user.id
        )
        
        if assignment:
            return jsonify({
                'success': True,
                'message': 'Chore cloned successfully',
                'assignment': {
                    'id': assignment.id,
                    'chore_name': original_chore.name,
                    'assigned_to': assignment.assigned_to.first_name
                }
            })
            
    except SQLAlchemyError as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    
    return jsonify({'success': False, 'message': 'Error cloning chore'}), 500

@app.route('/family/<int:family_id>/chores/assignment/<int:assignment_id>/unassign', methods=['POST'])
@login_required
def unassign_chore(family_id, assignment_id):
    user = User.get(session_token=session['session_token'])
    family = Family.get(id=family_id)
    
    if not family or not user.is_parent_in_family(family_id):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    assignment = ChoreAssignment.query.get(assignment_id)
    if not assignment or assignment.chore.family_id != family_id:
        return jsonify({'success': False, 'message': 'Assignment not found'}), 404
    
    try:
        # Just delete the assignment, not the chore
        db.session.delete(assignment)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Chore unassigned successfully'})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/family/<int:family_id>/chores/<int:chore_id>/delete', methods=['POST'])
@login_required
def delete_chore(family_id, chore_id):
    user = User.get(session_token=session['session_token'])
    family = Family.get(id=family_id)
    
    if not family or not user.is_parent_in_family(family_id):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    chore = Chore.query.get(chore_id)
    if not chore or chore.family_id != family_id:
        return jsonify({'success': False, 'message': 'Chore not found'}), 404
    
    try:
        # This will cascade delete all assignments too
        db.session.delete(chore)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Chore deleted successfully'})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/kid/dashboard')
@kid_required
def kid_dashboard():
    if 'viewing_as_child' in session:
        # Parent viewing as child - use child's data
        child_data = session['viewing_as_child']
        user = User.query.get(child_data['id'])
        family = Family.query.get(child_data['family_id'])
    else:
        # Regular child login
        user = User.get(session_token=session['session_token'])
        family = user.get_primary_family()
    
    if not family:
        flash("No family found", "danger")
        return redirect('/logout')
    
    # Get assignments and sort them by status, with eager loading of chore relationship
    assignments = ChoreAssignment.query\
        .filter_by(assigned_to_id=user.id)\
        .join(ChoreAssignment.chore)\
        .options(db.joinedload(ChoreAssignment.chore))\
        .all()
    
    context = {
        'user': user,
        'family': family,
        'pending_assignments': [a for a in assignments if a.status == 'pending'],
        'completed_assignments': [a for a in assignments if a.status == 'completed'],
        'approved_assignments': [a for a in assignments if a.status == 'approved']
    }
    return render_template('inside/chores/kid_dashboard.html', **context)

@app.route('/kid/store')
@kid_required
def kid_personal_store():
    user = User.get(session_token=session['session_token'])
    family = user.get_primary_family()
    
    personal_rewards = [r for r in family.rewards if not r.is_family_reward]
    
    context = {
        'user': user,
        'family': family,
        'rewards': personal_rewards
    }
    return render_template('inside/chores/personal_store.html', **context)

@app.route('/kid/family-store')
@kid_required
def kid_family_store():
    """View family rewards store as a child"""
    if 'viewing_as_child' in session:
        # Parent viewing as child - use child's data
        child_data = session['viewing_as_child']
        user = User.query.get(child_data['id'])
        family = Family.query.get(child_data['family_id'])
    else:
        # Regular child login
        user = User.get(session_token=session['session_token'])
        family = user.get_primary_family()
    
    if not family:
        flash("No family found", "danger")
        return redirect('/logout')
    
    family_rewards = [r for r in family.rewards if r.is_family_reward]
    
    context = {
        'user': user,
        'family': family,
        'rewards': family_rewards
    }
    return render_template('inside/chores/family_store.html', **context)

@app.route('/kid/rewards')
@kid_required
def kid_rewards_store():
    """View rewards store as a child"""
    if 'viewing_as_child' in session:
        # Parent viewing as child - use child's data
        child_data = session['viewing_as_child']
        user = User.query.get(child_data['id'])
        family = Family.query.get(child_data['family_id'])
    else:
        # Regular child login
        user = User.get(session_token=session['session_token'])
        family = user.get_primary_family()
    
    if not family:
        flash("No family found", "danger")
        return redirect('/logout')
    
    individual_rewards = [r for r in family.rewards if not r.is_family_reward]
    
    context = {
        'user': user,
        'family': family,
        'rewards': individual_rewards
    }
    return render_template('inside/chores/rewards_store.html', **context)

@app.route('/pin-login', methods=['POST'])
def pin_login_submit():
    email = request.form.get('email')
    pin = request.form.get('pin')
    
    user = User.verify_pin(email, pin)
    if not user:
        flash("Invalid email or PIN", "danger")
        return redirect('/pin-login')
    
    session['session_token'] = user.generate_session_token()
    flash(f"Welcome back, {user.first_name}!", "success")
    return redirect('/kid/dashboard')  # Redirect to kid dashboard instead of main dashboard

@app.route('/family/<int:family_id>/rewards/<int:reward_id>/redeem', methods=['POST'])
@login_required
def redeem_reward(family_id, reward_id):
    """Redeem a reward (individual or family)"""
    if 'viewing_as_child' in session:
        # Parent viewing as child - use child's data
        child_data = session['viewing_as_child']
        user = User.query.get(child_data['id'])
        family = Family.query.get(child_data['family_id'])
    else:
        # Regular child login
        user = User.get(session_token=session['session_token'])
        family = user.get_primary_family()
    
    if not family:
        return jsonify({'success': False, 'message': 'Family not found'}), 404
    
    reward = Reward.query.get(reward_id)
    if not reward or reward.family_id != family_id:
        return jsonify({'success': False, 'message': 'Invalid reward'}), 400
    
    if not reward.available:
        return jsonify({'success': False, 'message': 'Reward not available'}), 400
    
    # Check if user has enough coins/points
    if reward.is_family_reward:
        if family.total_points < reward.points_required:
            return jsonify({'success': False, 'message': 'Not enough family points'}), 400
    else:
        if user.coin_balance < reward.coin_cost:
            return jsonify({'success': False, 'message': 'Not enough coins'}), 400
    
    try:
        # Create redemption request
        redemption = RewardRedemption.create(
            reward_id=reward_id,
            user_id=user.id,
            status='pending'
        )
        
        if redemption:
            # Deduct coins/points
            if reward.is_family_reward:
                family.use_points(reward.points_required)
            else:
                user.use_coins(reward.coin_cost)
            
            flash("Redemption request submitted! Waiting for parent approval.", "success")
            return jsonify({'success': True})
            
    except SQLAlchemyError as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    
    return jsonify({'success': False, 'message': 'Error processing redemption'}), 500


# @app.route('/family/<int:family_id>/store/redeem/<int:reward_id>', methods=['POST'])
# @login_required
# def redeem_reward(family_id, reward_id):
#     """Redeem an individual reward"""
#     user = User.get(session_token=session['session_token'])
#     family = Family.get(id=family_id)
    
#     if not family or not any(m.family_id == family_id for m in user.family_memberships):
#         return jsonify({'success': False, 'message': 'Access denied'}), 403
    
#     reward = Reward.query.get(reward_id)
#     if not reward or reward.family_id != family_id:
#         return jsonify({'success': False, 'message': 'Invalid reward'}), 400
    
#     if not reward.available:
#         return jsonify({'success': False, 'message': 'Reward not available'}), 400
    
#     if user.coin_balance < reward.coin_cost:
#         return jsonify({'success': False, 'message': 'Not enough coins'}), 400
    
#     try:
#         redemption = RewardRedemption.create(
#             reward_id=reward_id,
#             user_id=user.id
#         )
        
#         if redemption:
#             flash("Redemption request submitted! Waiting for parent approval.", "success")
#             return jsonify({'success': True})
            
#     except SQLAlchemyError as e:
#         return jsonify({'success': False, 'message': str(e)}), 500
    
#     return jsonify({'success': False, 'message': 'Error processing redemption'}), 500