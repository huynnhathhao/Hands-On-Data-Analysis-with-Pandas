import argparse
import datetime as dt
import os
import logging

import login_attempt_simulator as sim

# Logging configuration
FORMAT = '[%(levelname)s] [ %(name)s ] %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger(os.path.basename(__file__))

def get_simulation_file_path(path_provided, directory, default_file):
    """Get the path to the file creating the directory and using the default if necessary."""
    if path_provided:
        file = path_provided
    else:
        if not os.path.exists(directory):
            os.mkdir(directory)
        file = os.path.join(directory, default_file)
    return file

def get_user_base_file_path(path_provided, default_file):
    """Get the path for a user_data directory file."""
    return get_simulation_file_path(path_provided, 'user_data', default_file)

def get_log_file_path(path_provided, default_file):
    """Get the path for a logs directory file."""
    return get_simulation_file_path(path_provided, 'logs', default_file)

if __name__ == '__main__':
    # command line argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "days", type=float,
        help="number of days to simulate from start"
    )
    parser.add_argument(
        "start_date", type=str,
        help="datetime to start in the form 'YYYY-MM-DD' or 'YYYY-MM-DD-HH'"
    )
    parser.add_argument(
        "-m", "--make", action='store_true', help="make userbase"
    )
    parser.add_argument(
        "-u", "--userbase", help="file to write the userbase to"
    )
    parser.add_argument(
        "-i", "--ip", help="file to write the user-ip address map to"
    )
    parser.add_argument(
        "-l", "--log", help="file to write the attempt log to"
    )
    parser.add_argument(
        "-hl", "--hacklog", help="file to write the hack log to"
    )
    args = parser.parse_args()

    if args.make:
        logger.warning('Creating new user base and mapping IP addresses to them.')

        user_base_file = get_user_base_file_path(args.userbase, 'user_base.txt')
        user_ip_mapping_file = get_user_base_file_path(args.ip, 'user_ips.json')

        # create usernames and write to file
        sim.utils.make_userbase(user_base_file)

        # create one or more IP addresses per user and save mapping to file
        valid_users = sim.utils.get_valid_users(user_base_file)
        sim.utils.save_user_ips(
            sim.utils.assign_ip_addresses(valid_users), user_ip_mapping_file
        )

    try:
        start = dt.datetime(*map(int, args.start_date.split('-')))
    except TypeError:
        logger.error('Start date must be in the format "YYYY-MM-DD"')
        raise
    except ValueError:
        logger.warning(
            f'Could not interpret {args.start_date}, '
            'using February 2, 2019 at 7AM as start instead'
        )
        start = dt.datetime(2019, 2, 1, 7, 0)

    end = start + dt.timedelta(days=args.days)

    try:
        logger.info(f'Simulating {args.days} days...')
        simulator = sim.LoginAttemptSimulator(user_ip_mapping_file, start, end)
        simulator.simulate(attack_prob=0.1, try_all_users_prob=0.65, vary_ips=False)

        # save logs
        logger.info('Saving logs')
        simulator.save_hack_log(get_log_file_path(args.hacklog, 'attacks.csv'))
        simulator.save_log(get_log_file_path(args.log, 'log.csv'))

        logger.info('All done!')
    except:
        logger.error('Oops! Something went wrong...')
