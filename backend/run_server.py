import argparse
from hki_signature_detection_api.server import run_app


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true',
                        help='Run server in debug mode')
    args = parser.parse_args()
    run_app(debug=args.debug, host='0.0.0.0')