"""AlayaNotes

Usage:
  main.py [run]
  main.py initdb
  main.py migrate
"""
from docopt import docopt
import subprocess
import os

from alayatodo import app


def _run_sql(filename):
    try:
        subprocess.check_output(
            "sqlite3 %s < %s" % (app.config['DATABASE'], filename),
            stderr=subprocess.STDOUT,
            shell=True
        )
    except subprocess.CalledProcessError, ex:
        print ex.output
        os.sys.exit(1)


if __name__ == '__main__':
    args = docopt(__doc__)
    if args['initdb']:
        _run_sql('resources/database.sql')
        _run_sql('resources/fixtures.sql')
        from resources import fixtures
        fixtures.main()
        print "AlayaTodo: Database initialized."
    elif args['migrate']:
        for migration in os.listdir('resources/migrations'):
            print 'Running migration "%s"' % migration
            _run_sql(os.path.join('resources/migrations', migration))
    else:
        app.run(use_reloader=True)
