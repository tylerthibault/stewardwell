from flask_app import app, db
from flask import render_template, redirect, session, request, flash, jsonify
from flask_app.config.helper import login_required
from flask_app.models.users import User
from flask_app.models.families import Family
from flask_app.models.family_members import FamilyMember, FamilyRole
import re
from datetime import datetime
import secrets
from sqlalchemy.exc import SQLAlchemyError
from dataclasses import asdict
import json

def serialize_member(member):
    """Convert a FamilyMember object to a dictionary for JSON serialization"""
    return {
        'id': member.id,
        'family_id': member.family_id,
        'role': member.role,
        'user': {
            'id': member.user.id,
            'first_name': member.user.first_name,
            'last_name': member.user.last_name,
            'email': member.user.email,
            'pin_code': member.user.pin_code,
            'is_child': member.user.is_child
        }
    }

@app.route('/family/create', methods=['GET', 'POST'])
@login_required
def create_family():
    user = User.get(session_token=session['session_token'])

    if request.method == 'GET':
        context = {
            'user': user
        }
        return render_template('inside/family/create.html', **context)
    
    family_name = request.form.get('family_name')
    if not family_name:
        flash("Family name is required", "danger")
        return redirect('/family/create')

    # Create the family
    family = Family.create(name=family_name)
    if not family:
        return redirect('/family/create')

    # Add the current user as a parent
    member = FamilyMember.create(user_id=user.id, family_id=family.id, role=FamilyRole.PARENT)
    
    if member:
        flash("Family created successfully!", "success")
        return redirect('/dashboard')
    return redirect('/family/create')

@app.route('/family/<int:family_id>')
@login_required
def family_dashboard(family_id):
    user = User.get(session_token=session['session_token'])
    family = Family.get(id=family_id)
    
    if not family:
        flash("Family not found", "danger")
        return redirect('/dashboard')
    
    # Check if user is a member of this family
    if not any(m.family_id == family_id for m in user.family_memberships):
        flash("You don't have access to this family", "danger")
        return redirect('/dashboard')
    
    context = {
        'user': user,
        'family': family,
        'members': family.members
    }
    return render_template('inside/family/dashboard.html', **context) 

@app.route('/family/<int:family_id>/invite', methods=['POST'])
@login_required
def invite_family_member(family_id):
    user = User.get(session_token=session['session_token'])
    family = Family.get(id=family_id)
    
    if not family:
        flash("Family not found", "danger")
        return redirect('/dashboard')
    
    # Verify the current user is a parent in this family
    if not user.is_parent_in_family(family_id):
        flash("You don't have permission to invite members", "danger")
        return redirect(f'/family/{family_id}')
    
    email = request.form.get('email')
    role = request.form.get('role')
    
    # Find the user to invite
    invited_user = User.get(email=email)
    if not invited_user:
        flash("No user found with that email address", "danger")
        return redirect(f'/family/{family_id}')
    
    # Check if user is already a member
    if any(m.family_id == family_id for m in invited_user.family_memberships):
        flash("This user is already a member of the family", "danger")
        return redirect(f'/family/{family_id}')
    
    # Create the membership
    member = FamilyMember.create(
        user_id=invited_user.id,
        family_id=family_id,
        role=role
    )
    
    if member:
        flash(f"Successfully added {invited_user.first_name} to the family!", "success")
    
    return redirect(f'/family/{family_id}')

@app.route('/family/<int:family_id>/member/add', methods=['GET', 'POST'])
@login_required
def add_family_member(family_id):
    user = User.get(session_token=session['session_token'])
    family = Family.get(id=family_id)
    
    if not family or not user.is_parent_in_family(family_id):
        flash("Access denied", "danger")
        return redirect('/dashboard')
    
    if request.method == 'GET':
        return render_template('inside/family/add_member.html', user=user, family=family)
    
    # Process form data
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    role = request.form.get('role')
    create_account = request.form.get('create_account') == 'on'
    
    if create_account:
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Generate email if not provided
        if not email:
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            email = f"{first_name.lower()}.{last_name.lower()}.{timestamp}@family.stewardwell.local"
        
        # Validate password
        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return redirect(f'/family/{family_id}/member/add')
        
        # Create user account
        new_user = User.create_one(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            confirm_password=confirm_password
        )
        
        if not new_user:
            return redirect(f'/family/{family_id}/member/add')
        
        # Create family membership
        member = FamilyMember.create(
            user_id=new_user.id,
            family_id=family_id,
            role=role
        )
        
    else:
        # Create user without login capability
        new_user = User.create_one(
            first_name=first_name,
            last_name=last_name,
            email=f"nologin.{first_name.lower()}.{last_name.lower()}@family.stewardwell.local",
            password=secrets.token_urlsafe(32),  # Random password since it won't be used
            confirm_password=secrets.token_urlsafe(32)
        )
        
        if not new_user:
            return redirect(f'/family/{family_id}/member/add')
        
        # Create family membership
        member = FamilyMember.create(
            user_id=new_user.id,
            family_id=family_id,
            role=role
        )
    
    if member:
        flash(f"Successfully added {first_name} to the family!", "success")
        return redirect(f'/family/{family_id}')
    
    return redirect(f'/family/{family_id}/member/add')

@app.route('/family/<int:family_id>/member/<int:member_id>/edit', methods=['POST'])
@login_required
def edit_family_member(family_id, member_id):
    user = User.get(session_token=session['session_token'])
    family = Family.get(id=family_id)
    
    if not family or not user.is_parent_in_family(family_id):
        flash("Access denied", "danger")
        return redirect(f'/family/{family_id}')
    
    member = FamilyMember.query.get(member_id)
    if not member or member.family_id != family_id:
        flash("Member not found", "danger")
        return redirect(f'/family/{family_id}')
    
    try:
        # Update member's user information
        member.user.first_name = request.form['first_name']
        member.user.last_name = request.form['last_name']
        
        # Update role
        new_role = request.form['role']
        member.role = new_role
        
        # Handle PIN for children
        if new_role == 'child':
            pin_code = request.form.get('pin_code')
            if pin_code:  # Only update if new PIN provided
                if not pin_code.isdigit() or len(pin_code) < 4 or len(pin_code) > 6:
                    flash("PIN must be 4-6 digits", "danger")
                    return redirect(f'/family/{family_id}')
                member.user.pin_code = pin_code
                member.user.is_child = True
        else:
            member.user.pin_code = None
            member.user.is_child = False
        
        db.session.commit()
        flash("Member updated successfully!", "success")
        return redirect(f'/family/{family_id}')
        
    except SQLAlchemyError as e:
        db.session.rollback()
        flash("Error updating member: " + str(e), "danger")
        return redirect(f'/family/{family_id}')

@app.route('/family/<int:family_id>/member/<int:member_id>/remove', methods=['POST'])
@login_required
def remove_family_member(family_id, member_id):
    user = User.get(session_token=session['session_token'])
    family = Family.get(id=family_id)
    
    if not family or not user.is_parent_in_family(family_id):
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    member = FamilyMember.query.get(member_id)
    if not member or member.family_id != family_id:
        return jsonify({'success': False, 'message': 'Member not found'}), 404
    
    try:
        # Store member info for response
        member_info = serialize_member(member)
        
        # Delete the member
        db.session.delete(member)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully removed {member_info["user"]["first_name"]} from the family',
            'removed_member': member_info
        })
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/family/<int:family_id>/settings')
@login_required
def family_settings(family_id):
    user = User.get(session_token=session['session_token'])
    family = Family.get(id=family_id)
    
    if not family or not any(m.family_id == family_id for m in user.family_memberships):
        flash("Access denied", "danger")
        return redirect('/dashboard')
    
    context = {
        'user': user,
        'family': family
    }
    return render_template('inside/family_settings.html', **context)

@app.route('/family/<int:family_id>/settings/update', methods=['POST'])
@login_required
def update_family_settings(family_id):
    user = User.get(session_token=session['session_token'])
    family = Family.get(id=family_id)
    
    if not family or not user.is_parent_in_family(family_id):
        flash("Access denied", "danger")
        return redirect('/dashboard')
    
    try:
        family.name = request.form['name']
        db.session.commit()
        flash("Family settings updated successfully!", "success")
    except SQLAlchemyError as e:
        db.session.rollback()
        flash("Error updating family settings: " + str(e), "danger")
    
    return redirect(url_for('family_settings', family_id=family_id))