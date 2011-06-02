from fabric.api import env, local, run, require, cd
from fabric.operations import _prefix_commands, _prefix_env_vars

# Host
env.disable_known_hosts = True # always fails for me without this
env.user = 'root'
env.hosts = ['dpaste.de']
env.proj_repo = 'git@github.com:bartTC/dpaste.de.git'

# Paths
env.root = '/opt/webapps/dpaste.de'
env.proj_root = env.root + '/src/dpastede'
env.pid_file = env.root + '/var/gunicorn.pid'
env.proj_bin = env.proj_root + '/pastebin/bin'
env.local_settings = env.proj_root + '/pastebin/conf/local/settings.py'
env.pip_file = env.proj_root + '/requirements.pip'

# ============================================================================
# Git
# ============================================================================

def push(remote=None, branch=None, reload=False):
    """Pushes the local git repo to the given remote and branch. Then pulls it
    o n the server."""
    remote = remote or 'origin'
    branch = branch or 'master'
    local('git push %s %s' % (remote, branch))
    with cd(env.proj_root):
        ve_run('git pull %s %s' % (remote, branch))
    if reload:
        restart()

def pushr(remote=None, branch=None, reload=True):
    push(remote, branch, reload)
    
def switch(branch):
    """Switch the repo branch which the server is using"""
    with cd(env.proj_root):
        ve_run('git checkout %s' % branch)
    restart()

def version():
    """Show last commit to repo on server"""
    with cd(env.proj_root):
        sshagent_run('git log -1')

# ============================================================================
# Server
# ============================================================================

def restart():
    """Kill the gunicorn process, Cherokee will start it upon request"""
    ve_run('kill `cat %s`' % env.pid_file)

def flush():
    """Flush memcache"""
    sshagent_run('/etc/init.d/memcached restart')
    
# ============================================================================
# Django
# ============================================================================

def update_reqs():
    """Update pip requirements"""
    ve_run('yes w | pip install -r %s' % env.pip_file)

def collect():
    manage('collectstatic --noinput')

def update(extreme=False):
    push()
    if extreme:
        update_reqs()
    collect()
    if extreme:
        flush()
    restart()

def debugon():
    """Turn debug mode on for the production server."""
    run("sed -i -e 's/^DEBUG = .*/DEBUG = True/' %s" % env.local_settings)
    restart()
    
def debugoff():
    """Turn debug mode on for the production server."""
    run("sed -i -e 's/^DEBUG = .*/DEBUG = False/' %s" % env.local_settings)
    restart()

# ============================================================================
# SSH funcs
# ============================================================================

def manage(cmd):
    return ve_run('python %s/manage.py %s' % (env.proj_bin, cmd))

def ve_run(cmd):
    """
    Helper function.
    Runs a command using the virtualenv environment
    """
    require('root')
    return sshagent_run('source %s/bin/activate; %s' % (env.root, cmd))

def sshagent_run(cmd):
    """
    Helper function.
    Runs a command with SSH agent forwarding enabled.

    Note:: Fabric (and paramiko) can't forward your SSH agent.
    This helper uses your system's ssh to do so.
    """
    # Handle context manager modifications
    wrapped_cmd = _prefix_commands(_prefix_env_vars(cmd), 'remote')
    try:
        host, port = env.host_string.split(':')
        return local(
            "ssh -p %s -A %s@%s '%s'" % (port, env.user, host, wrapped_cmd)
        )
    except ValueError:
        return local(
            "ssh -A %s@%s '%s'" % (env.user, env.host_string, wrapped_cmd)
        )