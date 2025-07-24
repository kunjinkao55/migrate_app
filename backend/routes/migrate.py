from flask import Blueprint, jsonify
from ..services.migrate import run_tests

bp = Blueprint('migrate', __name__, url_prefix='/api')

@bp.get('/run-test')
def run_test():
    run_tests()
    return jsonify({'msg': 'test executed'})