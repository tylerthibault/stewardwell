from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.modules.homeconomy import bp
from app.modules.homeconomy.models import Chore, CompletedChore, Reward, ClaimedReward, Goal
from app.utils.logger import ActivityLogger
from datetime import datetime

activity_logger = ActivityLogger('homeconomy')

@bp.route('/chores/verify/<int:completion_id>', methods=['POST'])
@login_required
def verify_chore(completion_id):
    """Verify a completed chore"""
    if not current_user.user_type == 'parent':
        activity_logger.log_error(
            current_user.id,
            'unauthorized_verification',
            'Non-parent user attempted to verify chore'
        )
        return jsonify({'error': 'Only parents can verify chores'}), 403

    completion = CompletedChore.query.get_or_404(completion_id)
    
    # Verify chore belongs to parent's family
    if completion.chore.family_id != current_user.family_id:
        activity_logger.log_error(
            current_user.id,
            'unauthorized_verification_access',
            f'Parent attempted to verify chore from another family: {completion_id}'
        )
        return jsonify({'error': 'Chore not found'}), 404

    try:
        # Mark as verified and award coins/points
        completion.verified = True
        completion.verified_by_id = current_user.id
        completion.verified_at = datetime.utcnow()
        
        # Award coins to child
        completion.child.coins += completion.chore.coins_reward
        
        # Add points to family total
        current_user.family.total_points += completion.chore.points_reward
        
        db.session.commit()

        activity_logger.log_activity(
            current_user.id,
            'chore_verified',
            {
                'completion_id': completion.id,
                'chore_id': completion.chore.id,
                'child_id': completion.child.id,
                'coins_awarded': completion.chore.coins_reward,
                'points_awarded': completion.chore.points_reward
            }
        )

        return jsonify({
            'message': 'Chore verified successfully!',
            'coins_awarded': completion.chore.coins_reward,
            'points_awarded': completion.chore.points_reward
        })

    except Exception as e:
        db.session.rollback()
        activity_logger.log_error(
            current_user.id,
            'verification_error',
            str(e)
        )
        return jsonify({'error': 'Error verifying chore'}), 500

@bp.route('/chores/reject/<int:completion_id>', methods=['POST'])
@login_required
def reject_chore(completion_id):
    """Reject a completed chore"""
    if not current_user.user_type == 'parent':
        activity_logger.log_error(
            current_user.id,
            'unauthorized_rejection',
            'Non-parent user attempted to reject chore'
        )
        return jsonify({'error': 'Only parents can reject chores'}), 403

    completion = CompletedChore.query.get_or_404(completion_id)
    
    # Verify chore belongs to parent's family
    if completion.chore.family_id != current_user.family_id:
        activity_logger.log_error(
            current_user.id,
            'unauthorized_rejection_access',
            f'Parent attempted to reject chore from another family: {completion_id}'
        )
        return jsonify({'error': 'Chore not found'}), 404

    try:
        # Delete the completion record
        db.session.delete(completion)
        db.session.commit()

        activity_logger.log_activity(
            current_user.id,
            'chore_rejected',
            {
                'completion_id': completion_id,
                'chore_id': completion.chore.id,
                'child_id': completion.child.id
            }
        )

        return jsonify({'message': 'Chore rejected successfully!'})

    except Exception as e:
        db.session.rollback()
        activity_logger.log_error(
            current_user.id,
            'rejection_error',
            str(e)
        )
        return jsonify({'error': 'Error rejecting chore'}), 500

@bp.route('/chores/verify-all', methods=['POST'])
@login_required
def verify_all_chores():
    """Verify all pending chores"""
    if not current_user.user_type == 'parent':
        activity_logger.log_error(
            current_user.id,
            'unauthorized_bulk_verification',
            'Non-parent user attempted to verify all chores'
        )
        return jsonify({'error': 'Only parents can verify chores'}), 403

    try:
        # Get all pending verifications for this family
        pending_verifications = CompletedChore.query.join(Chore).filter(
            Chore.family_id == current_user.family_id,
            CompletedChore.verified == False
        ).all()

        total_coins = 0
        total_points = 0

        for completion in pending_verifications:
            # Mark as verified
            completion.verified = True
            completion.verified_by_id = current_user.id
            completion.verified_at = datetime.utcnow()
            
            # Award coins to child
            completion.child.coins += completion.chore.coins_reward
            total_coins += completion.chore.coins_reward
            
            # Add points to family total
            current_user.family.total_points += completion.chore.points_reward
            total_points += completion.chore.points_reward

        db.session.commit()

        activity_logger.log_activity(
            current_user.id,
            'all_chores_verified',
            {
                'verifications_count': len(pending_verifications),
                'total_coins_awarded': total_coins,
                'total_points_awarded': total_points
            }
        )

        return jsonify({
            'message': 'All chores verified successfully!',
            'verifications_count': len(pending_verifications),
            'total_coins_awarded': total_coins,
            'total_points_awarded': total_points
        })

    except Exception as e:
        db.session.rollback()
        activity_logger.log_error(
            current_user.id,
            'bulk_verification_error',
            str(e)
        )
        return jsonify({'error': 'Error verifying chores'}), 500

@bp.route('/chores/create', methods=['POST'])
@login_required
def create_chore(chore_data):
    """Create a new chore"""
    if not current_user.user_type == 'parent':
        activity_logger.log_error(
            current_user.id,
            'unauthorized_creation',
            'Non-parent user attempted to create a chore'
        )
        return jsonify({'error': 'Only parents can create chores'}), 403

    try:
        # Create new chore instance
        new_chore = Chore(
            family_id=current_user.family_id,
            title=chore_data['title'],
            description=chore_data['description'],
            coins_reward=chore_data['coins_reward'],
            points_reward=chore_data['points_reward'],
            due_date=chore_data.get('due_date', None),
            created_at=datetime.utcnow()
        )

        # Add the new chore to the database
        db.session.add(new_chore)
        db.session.commit()

        # Log the activity
        activity_logger.log_activity(
            current_user.id,
            'chore_created',
            {
                'chore_id': new_chore.id,
                'chore_title': new_chore.title,
                'coins_reward': new_chore.coins_reward,
                'points_reward': new_chore.points_reward
            }
        )

        return jsonify({
            'message': 'Chore created successfully!',
            'chore_id': new_chore.id,
            'chore_title': new_chore.title,
            'coins_reward': new_chore.coins_reward,
            'points_reward': new_chore.points_reward
        })

    except Exception as e:
        db.session.rollback()
        activity_logger.log_error(
            current_user.id,
            'chore_creation_error',
            str(e)
        )
        return jsonify({'error': 'Error creating chore'}), 500