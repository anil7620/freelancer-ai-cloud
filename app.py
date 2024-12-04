from freelancing import freelancing
from freelancing.controllers import home_controller, admin_controller, freelancer_controller, jobposter_controller
from freelancing.controllers import  contract_controller, application_controller


if __name__ == "__main__":
     freelancing.run(host='0.0.0.0', port=5001, debug=True)