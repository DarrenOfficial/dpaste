from fabric.api import env, local, run, require, cd
from fabric.operations import _prefix_commands, _prefix_env_vars

env.disable_known_hosts = True # always fails for me without this
env.hosts = ['pastebin.dev.lincolnloop.com']
env.root = '/opt/webapps/pastebin'
env.proj_root = env.root + '/src/pastebin'
env.proj_repo = 'git@github.com:myuser/myrepo.git'
env.pip_file = env.proj_root + '/requirements.pip'


def deploy():
    """Update source, update pip requirements, syncdb, restart server"""
    update()
    update_reqs()
    syncdb()
    restart()


def switch(branch):
    """Switch the repo branch which the server is using"""
    with cd(env.proj_root):
        ve_run('git checkout %s' % branch)
    restart()


def version():
    """Show last commit to repo on server"""
    with cd(env.proj_root):
        sshagent_run('git log -1')


def restart():
    """Restart Apache process"""
    run('touch %s/etc/apache/django.wsgi' % env.root)


def update_reqs():
    """Update pip requirements"""
    ve_run('yes w | pip install -r %s' % env.pip_file)


def update():
    """Updates project source"""
    with cd(env.proj_root):
        sshagent_run('git pull')


def syncdb():
    """Run syncdb (along with any pending south migrations)"""
    ve_run('manage.py syncdb --migrate')


def clone():
    """Clone the repository for the first time"""
    with cd('%s/src' % env.root):
        sshagent_run('git clone %s' % env.proj_repo)
    ve_run('pip install -e %s' % env.proj_root)
    
    with cd('%s/pastebin/conf/local' % env.proj_root):
        run('ln -s ../dev/__init__.py')
        run('ln -s ../dev/settings.py')


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
