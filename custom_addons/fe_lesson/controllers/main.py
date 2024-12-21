from odoo import http
from odoo.http import request

class Lesson4Controller(http.Controller):
    @http.route('/', auth='public' , website=True)
    def homepage(self):
        # return homepage
        return request.render('fe_lesson.lesson4_homepage', {})
    
class FeedBackController(http.Controller):
    """
    Controller for handling feedback submissions.
    Methods
    -------
    feedback_submit(**kwargs)
        Handles the submission of feedback via a POST request.
    """
    """
    Handles the submission of feedback.
    Parameters
    ----------
    **kwargs : dict
        Arbitrary keyword arguments containing feedback details.
    Returns
    -------
    dict
        A dictionary containing the status and message of the feedback submission.
    """
    
    @http.route('/feedback/submit', auth='public', methods=['POST'], type='json', csrf=False)
    def feedback_submit(self, **kwargs):
        if 'description' not in kwargs:
            return {'status': 'fail', 'message': 'Description is required'}
        
        feedback = request.env['website.user.feedback'].sudo().create({
            'description': kwargs['description'],
        })
        
        return {'status': 'success', 'message': 'Feedback submitted successfully'}
