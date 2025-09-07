# -*- coding: utf-8 -*-
# Derived from ansible/plugins/connection/ssh.py (c) 2012, Michael DeHaan <michael.dehaan@gmail.com>
# Copyright (c) 2024 Nils Stein (@mietzen) <github.nstein@mailbox.org>
# Copyright (c) 2024 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
author: Nils Stein (@mietzen) <github.nstein@mailbox.org>
name: proxmox_pct_ssh
short_description: Run tasks in Proxmox LXC container instances using pct CLI via SSH
requirements:
  - ssh
description:
  - Run commands or put/fetch files to an existing Proxmox LXC container using pct CLI via SSH.
  - Uses the SSH binary to connect to the Proxmox host.
options:
  host:
    description: Address of the remote Proxmox host.
    default: inventory_hostname
    type: string
    vars:
      - name: inventory_hostname
      - name: ansible_host
      - name: ansible_ssh_host
  port:
    description: Remote port to connect to.
    type: int
    default: 22
    ini:
      - section: defaults
        key: remote_port
      - section: ssh_connection
        key: remote_port
    env:
      - name: ANSIBLE_REMOTE_PORT
      - name: ANSIBLE_SSH_REMOTE_PORT
    vars:
      - name: ansible_port
      - name: ansible_ssh_port
    keyword:
      - name: port
  remote_user:
    description:
      - User to login/authenticate as on the Proxmox host.
      - Can be set from the CLI via the C(--user) or C(-u) options.
    type: string
    vars:
      - name: ansible_user
      - name: ansible_ssh_user
    env:
      - name: ANSIBLE_REMOTE_USER
    ini:
      - section: defaults
        key: remote_user
    keyword:
      - name: remote_user
  password:
    description:
      - Authentication password for the O(remote_user). Can be supplied as CLI option.
    type: string
    vars:
      - name: ansible_password
      - name: ansible_ssh_pass
      - name: ansible_ssh_password
  password_mechanism:
    description: Mechanism to use for handling ssh password prompt
    type: string
    default: ssh_askpass
    choices:
      - ssh_askpass
      - sshpass
      - disable
    version_added: '2.19'
    env:
      - name: ANSIBLE_SSH_PASSWORD_MECHANISM
    ini:
      - {key: password_mechanism, section: ssh_connection}
    vars:
      - name: ansible_ssh_password_mechanism
  sshpass_prompt:
    description:
      - Password prompt that C(sshpass)/C(SSH_ASKPASS) should search for.
      - Supported by sshpass 1.06 and up when O(password_mechanism) set to V(sshpass).
    default: ''
    type: string
    ini:
      - section: 'ssh_connection'
        key: 'sshpass_prompt'
    env:
      - name: ANSIBLE_SSHPASS_PROMPT
    vars:
      - name: ansible_sshpass_prompt
  host_key_checking:
    description: "Set this to V(false) if you want to avoid host key checking by the underlying tools Ansible uses to connect to the host."
    type: boolean
    default: true
    env:
      - name: ANSIBLE_HOST_KEY_CHECKING
      - name: ANSIBLE_SSH_HOST_KEY_CHECKING
    ini:
      - section: defaults
        key: host_key_checking
      - section: ssh_connection
        key: host_key_checking
    vars:
      - name: ansible_host_key_checking
      - name: ansible_ssh_host_key_checking
  ssh_args:
    description: Arguments to pass to all SSH CLI tools.
    default: '-C -o ControlMaster=auto -o ControlPersist=60s'
    type: string
    ini:
      - section: 'ssh_connection'
        key: 'ssh_args'
    env:
      - name: ANSIBLE_SSH_ARGS
    vars:
      - name: ansible_ssh_args
  ssh_common_args:
    description: Common extra args for all SSH CLI tools.
    type: string
    ini:
      - section: 'ssh_connection'
        key: 'ssh_common_args'
    env:
      - name: ANSIBLE_SSH_COMMON_ARGS
    vars:
      - name: ansible_ssh_common_args
    cli:
      - name: ssh_common_args
    default: ''
  ssh_executable:
    default: ssh
    description:
      - This defines the location of the SSH binary. It defaults to V(ssh) which will use the first SSH binary available in $PATH.
    type: string
    env: [{name: ANSIBLE_SSH_EXECUTABLE}]
    ini:
    - {key: ssh_executable, section: ssh_connection}
    vars:
      - name: ansible_ssh_executable
  ssh_extra_args:
    description: Extra exclusive to the SSH CLI.
    type: string
    vars:
      - name: ansible_ssh_extra_args
    env:
    - name: ANSIBLE_SSH_EXTRA_ARGS
    ini:
    - key: ssh_extra_args
      section: ssh_connection
    cli:
    - name: ssh_extra_args
    default: ''
  private_key_file:
    description:
      - Path to private key file to use for authentication.
    type: string
    ini:
      - section: defaults
        key: private_key_file
    env:
      - name: ANSIBLE_PRIVATE_KEY_FILE
    vars:
      - name: ansible_private_key_file
      - name: ansible_ssh_private_key_file
    cli:
      - name: private_key_file
        option: "--private-key"
  timeout:
    default: 10
    description:
      - This is the default amount of time we will wait while establishing an SSH connection.
    env:
      - name: ANSIBLE_TIMEOUT
      - name: ANSIBLE_SSH_TIMEOUT
    ini:
      - key: timeout
        section: defaults
      - key: timeout
        section: ssh_connection
    vars:
      - name: ansible_ssh_timeout
    cli:
      - name: timeout
    type: integer
  use_tty:
    default: true
    description: add -tt to ssh commands to force tty allocation.
    env: [{name: ANSIBLE_SSH_USETTY}]
    ini:
    - {key: usetty, section: ssh_connection}
    type: bool
    vars:
      - name: ansible_ssh_use_tty
  control_path:
    description:
      - This is the location to save SSH's ControlPath sockets, it uses SSH's variable substitution.
      - Since 2.3, if null (default), ansible will generate a unique hash. Use ``%(directory)s`` to indicate where to use the control dir path setting.
    type: string
    env:
      - name: ANSIBLE_SSH_CONTROL_PATH
    ini:
      - key: control_path
        section: ssh_connection
    vars:
      - name: ansible_control_path
  control_path_dir:
    default: ~/.ansible/cp
    description:
      - This sets the directory to use for ssh control path if the control path setting is null.
      - Also, provides the ``%(directory)s`` variable for the control path setting.
    type: string
    env:
      - name: ANSIBLE_SSH_CONTROL_PATH_DIR
    ini:
      - section: ssh_connection
        key: control_path_dir
    vars:
      - name: ansible_control_path_dir
  reconnection_retries:
    description:
      - Number of attempts to connect.
      - Ansible retries connections only if it gets an SSH error with a return code of 255.
    default: 0
    type: integer
    env:
      - name: ANSIBLE_SSH_RETRIES
    ini:
      - section: connection
        key: retries
      - section: ssh_connection
        key: retries
    vars:
      - name: ansible_ssh_retries
  vmid:
    description:
      - LXC Container ID
    type: int
    required: true
    vars:
      - name: proxmox_vmid
  proxmox_become_method:
    description:
      - Become command used in proxmox
    type: str
    default: sudo
    vars:
      - name: proxmox_become_method
notes:
  - >
    When NOT using this plugin as root, you need to have a become mechanism,
    e.g. C(sudo), installed on Proxmox and setup so we can run it without prompting for the password.
    Inside the container, we need a shell, for example C(sh) and the C(cat) command to be available in the C(PATH) for this plugin to work.
"""

EXAMPLES = r"""
# Same examples as the original plugin...
"""

import argparse
import collections.abc as c
import contextlib
import errno
import fcntl
import hashlib
import io
import json
import os
import pathlib
import pty
import re
import selectors
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import typing as t
from functools import wraps
from multiprocessing.shared_memory import SharedMemory

from ansible.errors import (
    AnsibleAuthenticationFailure,
    AnsibleConnectionFailure,
    AnsibleError,
    AnsibleFileNotFound,
)
from ansible.module_utils.common.text.converters import to_bytes, to_native, to_text
from ansible.plugins.connection import ConnectionBase, BUFSIZE
from ansible.utils.display import Display
from ansible.utils.path import unfrackpath, makedirs_safe

display = Display()

# error messages that indicate 255 return code is not from ssh itself.
b_NOT_SSH_ERRORS = (b'Traceback (most recent call last):',  # Python-2.6 when there's an exception
                                                            #   while invoking a script via -m
                    b'PHP Parse error:',                    # Php always returns with error
                    b'chmod: invalid mode',                 # chmod, but really only on AIX
                    b'chmod: A flag or octal number is not correct.',    # chmod, other AIX
                    )

SSHPASS_AVAILABLE = None
SSH_DEBUG = re.compile(r'^debug\d+: .*')

_HAS_RESOURCE_TRACK = sys.version_info[:2] >= (3, 13)

SSH_ASKPASS_DEFAULT_PROMPT = 'assword'


class AnsibleControlPersistBrokenPipeError(AnsibleError):
    """ ControlPersist broken pipe """
    pass


def _handle_error(
    remaining_retries: int,
    command: bytes,
    return_tuple: tuple[int, bytes, bytes],
    no_log: bool,
    host: str,
    display: Display = display,
) -> None:

    # sshpass errors
    if command == b'sshpass':
        # Error 5 is invalid/incorrect password. Raise an exception to prevent retries from locking the account.
        if return_tuple[0] == 5:
            msg = 'Invalid/incorrect username/password. Skipping remaining {0} retries to prevent account lockout:'.format(remaining_retries)
            if remaining_retries <= 0:
                msg = 'Invalid/incorrect password:'
            if no_log:
                msg = '{0} <error censored due to no log>'.format(msg)
            else:
                msg = '{0} {1}'.format(msg, to_native(return_tuple[2]).rstrip())
            raise AnsibleAuthenticationFailure(msg)

        # sshpass returns codes are 1-6. We handle 5 previously, so this catches other scenarios.
        elif return_tuple[0] in [1, 2, 3, 4, 6]:
            msg = 'sshpass error:'
            if no_log:
                msg = '{0} <error censored due to no log>'.format(msg)
            else:
                details = to_native(return_tuple[2]).rstrip()
                if "sshpass: invalid option -- 'P'" in details:
                    details = 'Installed sshpass version does not support customized password prompts. ' \
                              'Upgrade sshpass to use sshpass_prompt, or otherwise switch to ssh keys.'
                    raise AnsibleError('{0} {1}'.format(msg, details))
                msg = '{0} {1}'.format(msg, details)
            raise AnsibleConnectionFailure(msg)

    if return_tuple[0] == 255:
        SSH_ERROR = True
        for signature in b_NOT_SSH_ERRORS:
            # 1 == stout, 2 == stderr
            if signature in return_tuple[1] or signature in return_tuple[2]:
                SSH_ERROR = False
                break

        if SSH_ERROR:
            msg = "Failed to connect to the host via ssh:"
            if no_log:
                msg = '{0} <error censored due to no log>'.format(msg)
            else:
                msg = '{0} {1}'.format(msg, to_native(return_tuple[2]).rstrip())
            raise AnsibleConnectionFailure(msg)

    # For other errors, no exception is raised so the connection is retried and we only log the messages
    if 1 <= return_tuple[0] <= 254:
        msg = u"Failed to connect to the host via ssh:"
        if no_log:
            msg = u'{0} <error censored due to no log>'.format(msg)
        else:
            msg = u'{0} {1}'.format(msg, to_text(return_tuple[2]).rstrip())
        display.vvv(msg, host=host)


def _ssh_retry[**P](
    func: c.Callable[t.Concatenate[Connection, P], tuple[int, bytes, bytes]],
) -> c.Callable[t.Concatenate[Connection, P], tuple[int, bytes, bytes]]:
    """
    Decorator to retry ssh in the case of a connection failure
    """
    @wraps(func)
    def wrapped(self: Connection, *args: P.args, **kwargs: P.kwargs) -> tuple[int, bytes, bytes]:
        remaining_tries = int(self.get_option('reconnection_retries')) + 1
        cmd_summary = u"%s..." % to_text(args[0])
        conn_password = self.get_option('password') or self._play_context.password
        is_sshpass = self.get_option('password_mechanism') == 'sshpass'
        
        for attempt in range(remaining_tries):
            cmd = t.cast(list[bytes], args[0])
            if attempt != 0 and is_sshpass and conn_password and isinstance(cmd, list):
                # If this is a retry, the fd/pipe for sshpass is closed, and we need a new one
                self.sshpass_pipe = os.pipe()
                cmd[1] = b'-d' + to_bytes(self.sshpass_pipe[0], nonstring='simplerepr', errors='surrogate_or_strict')

            try:
                try:
                    return_tuple = func(self, *args, **kwargs)
                    # TODO: this should come from task
                    if self._play_context.no_log:
                        display.vvv(u'rc=%s, stdout and stderr censored due to no log' % return_tuple[0], host=self.host)
                    else:
                        display.vvv(str(return_tuple), host=self.host)
                    # 0 = success
                    # 1-254 = remote command return code
                    # 255 could be a failure from the ssh command itself
                except (AnsibleControlPersistBrokenPipeError):
                    # Retry one more time because of the ControlPersist broken pipe (see #16731)
                    cmd = t.cast(list[bytes], args[0])
                    if is_sshpass and conn_password and isinstance(cmd, list):
                        # This is a retry, so the fd/pipe for sshpass is closed, and we need a new one
                        self.sshpass_pipe = os.pipe()
                        cmd[1] = b'-d' + to_bytes(self.sshpass_pipe[0], nonstring='simplerepr', errors='surrogate_or_strict')
                    display.vvv(u"RETRYING BECAUSE OF CONTROLPERSIST BROKEN PIPE")
                    return_tuple = func(self, *args, **kwargs)

                remaining_retries = remaining_tries - attempt - 1
                _handle_error(remaining_retries, cmd[0], return_tuple, self._play_context.no_log, self.host)

                break

            # 5 = Invalid/incorrect password from sshpass
            except AnsibleAuthenticationFailure:
                # Raising this exception, which is subclassed from AnsibleConnectionFailure, prevents further retries
                raise

            except (AnsibleConnectionFailure, Exception) as e:
                if attempt == remaining_tries - 1:
                    raise
                else:
                    pause = 2 ** attempt - 1
                    if pause > 30:
                        pause = 30

                    if isinstance(e, AnsibleConnectionFailure):
                        msg = u"ssh_retry: attempt: %d, ssh return code is 255. cmd (%s), pausing for %d seconds" % (attempt + 1, cmd_summary, pause)
                    else:
                        msg = (u"ssh_retry: attempt: %d, caught exception(%s) from cmd (%s), "
                               u"pausing for %d seconds" % (attempt + 1, to_text(e), cmd_summary, pause))

                    display.vv(msg, host=self.host)

                    time.sleep(pause)
                    continue

        return return_tuple
    return wrapped


def _clean_shm(func):
    def inner(self, *args, **kwargs):
        try:
            ret = func(self, *args, **kwargs)
        finally:
            if self.shm:
                self.shm.close()
                with contextlib.suppress(FileNotFoundError):
                    self.shm.unlink()
                    if not _HAS_RESOURCE_TRACK:
                        # deprecated: description='unneeded due to track argument for SharedMemory' python_version='3.12'
                        # There is a resource tracking issue where the resource is deleted, but tracking still has a record
                        # This will effectively overwrite the record and remove it
                        SharedMemory(name=self.shm.name, create=True, size=1).unlink()
        return ret
    return inner


class Connection(ConnectionBase):
    """ SSH based connections to Proxmox LXC containers via pct """

    transport = 'community.proxmox.proxmox_pct_ssh'
    has_pipelining = True

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super(Connection, self).__init__(*args, **kwargs)

        # TODO: all should come from get_option(), but not might be set at this point yet
        self.host = self._play_context.remote_addr
        self.port = self._play_context.port
        self.user = self._play_context.remote_user
        self.control_path: str | None = None
        self.control_path_dir: str | None = None
        self.shm: SharedMemory | None = None
        self.sshpass_pipe: tuple[int, int] | None = None

        # parser to discover 'passed options', used later on for pipelining resolution
        self._tty_parser = argparse.ArgumentParser()
        self._tty_parser.add_argument('-t', action='count')
        self._tty_parser.add_argument('-o', action='append')

    def _connect(self) -> Connection:
        return self

    @staticmethod
    def _create_control_path(
        host: str | None,
        port: int | None,
        user: str | None,
        connection: ConnectionBase | None = None,
        pid: int | None = None,
    ) -> str:
        """Make a hash for the controlpath based on con attributes"""
        pstring = '%s-%s-%s' % (host, port, user)
        if connection:
            pstring += '-%s' % connection
        if pid:
            pstring += '-%s' % to_text(pid)
        m = hashlib.sha1()
        m.update(to_bytes(pstring))
        digest = m.hexdigest()
        cpath = '%(directory)s/' + digest[:10]
        return cpath

    @staticmethod
    def _sshpass_available() -> bool:
        global SSHPASS_AVAILABLE

        # We test once if sshpass is available, and remember the result.
        if SSHPASS_AVAILABLE is None:
            SSHPASS_AVAILABLE = shutil.which('sshpass') is not None

        return SSHPASS_AVAILABLE

    @staticmethod
    def _persistence_controls(b_command: list[bytes]) -> tuple[bool, bool]:
        """
        Takes a command array and scans it for ControlPersist and ControlPath
        settings and returns two booleans indicating whether either was found.
        """
        controlpersist = False
        controlpath = False

        for b_arg in (a.lower() for a in b_command):
            if b'controlpersist' in b_arg:
                controlpersist = True
            elif b'controlpath' in b_arg:
                controlpath = True

        return controlpersist, controlpath

    def _add_args(self, b_command: list[bytes], b_args: t.Iterable[bytes], explanation: str) -> None:
        """
        Adds arguments to the ssh command and displays a caller-supplied explanation of why.
        """
        display.vvvvv(u'SSH: %s: (%s)' % (explanation, ')('.join(to_text(a) for a in b_args)), host=self.host)
        b_command += b_args

    def _build_pct_command(self, cmd: str) -> str:
        """Build the pct command to execute inside the container"""
        pct_cmd = ['/usr/sbin/pct', 'exec', str(self.get_option('vmid')), '--', cmd]
        if self.get_option('remote_user') != 'root':
            pct_cmd = [self.get_option('proxmox_become_method')] + pct_cmd
            display.vvv(f'INFO Running as non root user: {self.get_option("remote_user")}, trying to run pct with become method: ' +
                        f'{self.get_option("proxmox_become_method")}',
                        host=self.get_option('host'))
        return ' '.join(pct_cmd)

    def _init_shm(self) -> dict[str, t.Any]:
        env = os.environ.copy()
        popen_kwargs: dict[str, t.Any] = {}

        if self.get_option('password_mechanism') != 'ssh_askpass':
            return popen_kwargs

        conn_password = self.get_option('password') or self._play_context.password
        if not conn_password:
            return popen_kwargs

        kwargs = {}
        if _HAS_RESOURCE_TRACK:
            kwargs['track'] = False
        self.shm = shm = SharedMemory(create=True, size=16384, **kwargs)  # type: ignore[arg-type]

        sshpass_prompt = self.get_option('sshpass_prompt')
        if not sshpass_prompt:
            sshpass_prompt = SSH_ASKPASS_DEFAULT_PROMPT

        data = json.dumps({
            'password': conn_password,
            'prompt': sshpass_prompt,
        }).encode('utf-8')
        shm.buf[:len(data)] = bytearray(data)
        shm.close()

        env['_ANSIBLE_SSH_ASKPASS_SHM'] = str(self.shm.name)
        adhoc = pathlib.Path(sys.argv[0]).with_name('ansible')
        env['SSH_ASKPASS'] = str(adhoc) if adhoc.is_file() else 'ansible'

        # SSH_ASKPASS_REQUIRE was added in openssh 8.4, prior to 8.4 there must be no tty, and DISPLAY must be set
        env['SSH_ASKPASS_REQUIRE'] = 'force'
        if not env.get('DISPLAY'):
            env['DISPLAY'] = '-'

        popen_kwargs['env'] = env
        popen_kwargs['start_new_session'] = True

        return popen_kwargs

    def _build_command(self, binary: str, subsystem: str, *other_args: bytes | str) -> list[bytes]:
        """
        Build the SSH command to execute the pct command on the Proxmox host
        """
        b_command = []
        conn_password = self.get_option('password') or self._play_context.password
        password_mechanism = self.get_option('password_mechanism')

        # Setup sshpass if needed
        if password_mechanism == 'sshpass' and conn_password:
            if not self._sshpass_available():
                raise AnsibleError("to use the password_mechanism=sshpass, you must install the sshpass program")

            self.sshpass_pipe = os.pipe()
            b_command += [b'sshpass', b'-d' + to_bytes(self.sshpass_pipe[0], nonstring='simplerepr', errors='surrogate_or_strict')]

            password_prompt = self.get_option('sshpass_prompt')
            if password_prompt:
                b_command += [b'-P', to_bytes(password_prompt, errors='surrogate_or_strict')]

        b_command += [to_bytes(binary, errors='surrogate_or_strict')]

        # Add SSH arguments
        ssh_args = self.get_option('ssh_args')
        if ssh_args:
            b_args = [to_bytes(a, errors='surrogate_or_strict') for a in
                      self._split_ssh_args(ssh_args)]
            self._add_args(b_command, b_args, u"ansible.cfg set ssh_args")

        # Host key checking
        if self.get_option('host_key_checking') is False:
            b_args = (b"-o", b"StrictHostKeyChecking=no")
            self._add_args(b_command, b_args, u"host_key_checking disabled")

        # Port
        self.port = self.get_option('port')
        if self.port is not None:
            b_args = (b"-o", b"Port=" + to_bytes(self.port, nonstring='simplerepr', errors='surrogate_or_strict'))
            self._add_args(b_command, b_args, u"port set")

        # Private key
        if key := self.get_option('private_key_file'):
            b_args = (b"-o", b'IdentityFile="' + to_bytes(os.path.expanduser(key), errors='surrogate_or_strict') + b'"')
            self._add_args(b_command, b_args, u"private_key_file set")

        # User
        self.user = self.get_option('remote_user')
        if self.user:
            self._add_args(
                b_command,
                (b"-o", b'User="%s"' % to_bytes(self.user, errors='surrogate_or_strict')),
                u"remote_user set"
            )

        # Timeout
        timeout = self.get_option('timeout')
        self._add_args(
            b_command,
            (b"-o", b"ConnectTimeout=" + to_bytes(timeout, errors='surrogate_or_strict', nonstring='simplerepr')),
            u"timeout set"
        )

        # Add common and extra args
        for opt in (u'ssh_common_args', u'ssh_extra_args'):
            attr = self.get_option(opt)
            if attr is not None:
                b_args = [to_bytes(a, errors='surrogate_or_strict') for a in self._split_ssh_args(attr)]
                self._add_args(b_command, b_args, u"Set %s" % opt)

        # ControlPersist handling
        controlpersist, controlpath = self._persistence_controls(b_command)
        if controlpersist:
            self._persistent = True

            if not controlpath:
                self.control_path_dir = self.get_option('control_path_dir')
                cpdir = unfrackpath(self.control_path_dir)
                b_cpdir = to_bytes(cpdir, errors='surrogate_or_strict')

                makedirs_safe(b_cpdir, 0o700)
                if not os.access(b_cpdir, os.W_OK):
                    raise AnsibleError("Cannot write to ControlPath %s" % to_native(cpdir))

                self.control_path = self.get_option('control_path')
                if not self.control_path:
                    self.control_path = self._create_control_path(
                        self.host,
                        self.port,
                        self.user
                    )
                b_args = (b"-o", b'ControlPath="%s"' % to_bytes(self.control_path % dict(directory=cpdir), errors='surrogate_or_strict'))
                self._add_args(b_command, b_args, u"added ControlPath")

        if password_mechanism == "ssh_askpass":
            self._add_args(
                b_command,
                (b"-o", b"NumberOfPasswordPrompts=1"),
                "Restrict number of password prompts",
            )

        # Add caller-supplied extras
        if other_args:
            b_command += [to_bytes(a) for a in other_args]

        return b_command

    def _send_initial_data(self, fh: io.IOBase, in_data: bytes, ssh_process: subprocess.Popen) -> None:
        """
        Writes initial data to the stdin filehandle of the subprocess and closes it.
        """
        display.debug(u'Sending initial data')

        try:
            fh.write(to_bytes(in_data))
            fh.close()
        except OSError as ex:
            time.sleep(0.001)
            ssh_process.poll()
            if getattr(ssh_process, 'returncode', None) is None:
                raise AnsibleConnectionFailure(f'Data could not be sent to remote host {self.host!r}. Make sure this host can be reached over SSH.') from ex

        display.debug(u'Sent initial data (%d bytes)' % len(in_data))

    @staticmethod
    def _terminate_process(p: subprocess.Popen) -> None:
        """ Terminate a process, ignoring errors """
        try:
            p.terminate()
        except OSError:
            pass

    def _examine_output(self, source: str, state: str, b_chunk: bytes, sudoable: bool) -> tuple[bytes, bytes]:
        """
        Takes a string, extracts complete lines from it, tests to see if they
        are a prompt, error message, etc., and sets appropriate flags in self.
        Prompt and success lines are removed.
        """
        output = []
        for b_line in b_chunk.splitlines(True):
            display_line = to_text(b_line).rstrip('\r\n')
            suppress_output = False

            if SSH_DEBUG.match(display_line):
                # skip lines from ssh debug output to avoid false matches
                pass
            elif self.become.expect_prompt() and self.become.check_password_prompt(b_line):
                display.debug(u"become_prompt: (source=%s, state=%s): '%s'" % (source, state, display_line))
                self._flags['become_prompt'] = True
                suppress_output = True
            elif self.become.success and self.become.check_success(b_line):
                display.debug(u"become_success: (source=%s, state=%s): '%s'" % (source, state, display_line))
                self._flags['become_success'] = True
                suppress_output = True
            elif sudoable and self.become.check_incorrect_password(b_line):
                display.debug(u"become_error: (source=%s, state=%s): '%s'" % (source, state, display_line))
                self._flags['become_error'] = True
            elif sudoable and self.become.check_missing_password(b_line):
                display.debug(u"become_nopasswd_error: (source=%s, state=%s): '%s'" % (source, state, display_line))
                self._flags['become_nopasswd_error'] = True

            if not suppress_output:
                output.append(b_line)

        # The chunk we read was most likely a series of complete lines, but just
        # in case the last line was incomplete (and not a prompt, which we would
        # have removed from the output), we retain it to be processed with the
        # next chunk.
        remainder = b''
        if output and not output[-1].endswith(b'\n'):
            remainder = output[-1]
            output = output[:-1]

        return b''.join(output), remainder

    @_clean_shm
    def _bare_run(self, cmd: list[bytes], in_data: bytes | None, sudoable: bool = True, checkrc: bool = True) -> tuple[int, bytes, bytes]:
        """
        Starts the command and communicates with it until it ends.
        """
        # We don't use _shell.quote as this is run on the controller and independent from the shell plugin chosen
        display_cmd = u' '.join(shlex.quote(to_text(c)) for c in cmd)
        display.vvv(u'SSH: EXEC {0}'.format(display_cmd), host=self.host)

        conn_password = self.get_option('password') or self._play_context.password
        password_mechanism = self.get_option('password_mechanism')

        # Start the given command. If we don't need to pipeline data, we can try
        # to use a pseudo-tty (ssh will have been invoked with -tt). If we are
        # pipelining data, or can't create a pty, we fall back to using plain
        # old pipes.
        p = None

        if isinstance(cmd, (str, bytes)):
            cmd = to_bytes(cmd)
        else:
            cmd = list(map(to_bytes, cmd))

        popen_kwargs = self._init_shm()

        if self.sshpass_pipe:
            popen_kwargs['pass_fds'] = self.sshpass_pipe

        if not in_data:
            try:
                # Make sure stdin is a proper pty to avoid tcgetattr errors
                master, slave = pty.openpty()
                p = subprocess.Popen(cmd, stdin=slave, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **popen_kwargs)
                stdin = os.fdopen(master, 'wb', 0)
                os.close(slave)
            except OSError:
                p = None

        if not p:
            try:
                p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, **popen_kwargs)
                stdin = p.stdin  # type: ignore[assignment]
            except OSError as ex:
                raise AnsibleError('Unable to execute ssh command line on a controller.') from ex

        if password_mechanism == 'sshpass' and conn_password:
            os.close(self.sshpass_pipe[0])
            try:
                os.write(self.sshpass_pipe[1], to_bytes(conn_password) + b'\n')
            except OSError as e:
                # Ignore broken pipe errors if the sshpass process has exited.
                if e.errno != errno.EPIPE or p.poll() is None:
                    raise
            os.close(self.sshpass_pipe[1])

        # SSH state machine
        states = [
            'awaiting_prompt', 'awaiting_escalation', 'ready_to_send', 'awaiting_exit'
        ]

        # Are we requesting privilege escalation? 
        state = states.index('ready_to_send')
        if to_bytes(self.get_option('ssh_executable')) in cmd and sudoable:
            prompt = getattr(self.become, 'prompt', None)
            if prompt:
                state = states.index('awaiting_prompt')
                display.debug(u'Initial state: %s: %s' % (states[state], to_text(prompt)))
            elif self.become and self.become.success:
                state = states.index('awaiting_escalation')
                display.debug(u'Initial state: %s: %s' % (states[state], to_text(self.become.success)))

        # Accumulate stdout and stderr output
        b_stdout = b_stderr = b''
        b_tmp_stdout = b_tmp_stderr = b''

        self._flags = dict(
            become_prompt=False, become_success=False,
            become_error=False, become_nopasswd_error=False
        )

        timeout = 2 + self.get_option('timeout')
        for fd in (p.stdout, p.stderr):
            fcntl.fcntl(fd, fcntl.F_SETFL, fcntl.fcntl(fd, fcntl.F_GETFL) | os.O_NONBLOCK)

        selector = selectors.DefaultSelector()
        selector.register(p.stdout, selectors.EVENT_READ)
        selector.register(p.stderr, selectors.EVENT_READ)

        # If we can send initial data without waiting for anything, we do so
        # before we start polling
        if states[state] == 'ready_to_send' and in_data:
            self._send_initial_data(stdin, in_data, p)
            state += 1

        try:
            while True:
                poll = p.poll()
                events = selector.select(timeout)

                # We pay attention to timeouts only while negotiating a prompt.
                if not events:
                    # We timed out
                    if state <= states.index('awaiting_escalation'):
                        if poll is not None:
                            break
                        self._terminate_process(p)
                        raise AnsibleConnectionFailure('Timeout (%ds) waiting for privilege escalation prompt: %s' % (timeout, to_native(b_stdout)))

                    display.vvvvv(f'SSH: Timeout ({timeout}s) waiting for the output', host=self.host)

                # Read whatever output is available on stdout and stderr
                for key, event in events:
                    if key.fileobj == p.stdout:
                        b_chunk = p.stdout.read()
                        if b_chunk == b'':
                            selector.unregister(p.stdout)
                            timeout = 1
                        b_tmp_stdout += b_chunk
                        display.debug(u"stdout chunk (state=%s):\n>>>%s<<<\n" % (state, to_text(b_chunk)))
                    elif key.fileobj == p.stderr:
                        b_chunk = p.stderr.read()
                        if b_chunk == b'':
                            selector.unregister(p.stderr)
                        b_tmp_stderr += b_chunk
                        display.debug("stderr chunk (state=%s):\n>>>%s<<<\n" % (state, to_text(b_chunk)))

                # Examine the output line-by-line until we have negotiated any
                # privilege escalation prompt and subsequent success/error message.
                if state < states.index('ready_to_send'):
                    if b_tmp_stdout:
                        b_output, b_unprocessed = self._examine_output('stdout', states[state], b_tmp_stdout, sudoable)
                        b_stdout += b_output
                        b_tmp_stdout = b_unprocessed

                    if b_tmp_stderr:
                        b_output, b_unprocessed = self._examine_output('stderr', states[state], b_tmp_stderr, sudoable)
                        b_stderr += b_output
                        b_tmp_stderr = b_unprocessed
                else:
                    b_stdout += b_tmp_stdout
                    b_stderr += b_tmp_stderr
                    b_tmp_stdout = b_tmp_stderr = b''

                # Handle privilege escalation prompts
                if states[state] == 'awaiting_prompt':
                    if self._flags['become_prompt']:
                        display.debug(u'Sending become_password in response to prompt')
                        become_pass = self.become.get_option('become_pass', playcontext=self._play_context)
                        stdin.write(to_bytes(become_pass, errors='surrogate_or_strict') + b'\n')
                        stdin.flush()
                        self._flags['become_prompt'] = False
                        state += 1
                    elif self._flags['become_success']:
                        state += 1

                # Wait for escalation success/failure
                if states[state] == 'awaiting_escalation':
                    if self._flags['become_success']:
                        display.vvv(u'Escalation succeeded', host=self.host)
                        self._flags['become_success'] = False
                        state += 1
                    elif self._flags['become_error']:
                        display.vvv(u'Escalation failed', host=self.host)
                        self._terminate_process(p)
                        self._flags['become_error'] = False
                        raise AnsibleError('Incorrect %s password' % self.become.name)
                    elif self._flags['become_nopasswd_error']:
                        display.vvv(u'Escalation requires password', host=self.host)
                        self._terminate_process(p)
                        self._flags['become_nopasswd_error'] = False
                        raise AnsibleError('Missing %s password' % self.become.name)
                    elif self._flags['become_prompt']:
                        display.vvv(u'Escalation prompt repeated', host=self.host)
                        self._terminate_process(p)
                        self._flags['become_prompt'] = False
                        raise AnsibleError('Incorrect %s password' % self.become.name)

                # Send initial data once escalation is handled
                if states[state] == 'ready_to_send':
                    if in_data:
                        self._send_initial_data(stdin, in_data, p)
                    state += 1

                # Check if process has exited
                if poll is not None:
                    if not selector.get_map() or not events:
                        break
                    timeout = 0
                    continue

                elif not selector.get_map():
                    p.wait()
                    break

        finally:
            selector.close()
            stdin.close()
            p.stdout.close()
            p.stderr.close()

        # Check for specific error conditions
        conn_password = self.get_option('password') or self._play_context.password
        hostkey_fail = any((
            (cmd[0] == b"sshpass" and p.returncode == 6),
            b"read_passphrase: can't open /dev/tty" in b_stderr,
            b"Host key verification failed" in b_stderr,
        ))
        if password_mechanism and self.get_option('host_key_checking') and conn_password and hostkey_fail:
            raise AnsibleError('Using a SSH password instead of a key is not possible because Host Key checking is enabled. '
                               'Please add this host\'s fingerprint to your known_hosts file to manage this host.')

        controlpersisterror = b'Bad configuration option: ControlPersist' in b_stderr or b'unknown configuration option: ControlPersist' in b_stderr
        if p.returncode != 0 and controlpersisterror:
            raise AnsibleError('using -c ssh on certain older ssh versions may not support ControlPersist, set ANSIBLE_SSH_ARGS="" '
                               '(or ssh_args in [ssh_connection] section of the config file) before running again')

        # Check for ControlPersist broken pipe
        controlpersist_broken_pipe = b'mux_client_hello_exchange: write packet: Broken pipe' in b_stderr
        if p.returncode == 255:
            additional = to_native(b_stderr)
            if controlpersist_broken_pipe:
                raise AnsibleControlPersistBrokenPipeError('Data could not be sent because of ControlPersist broken pipe: %s' % additional)
            elif in_data and checkrc:
                raise AnsibleConnectionFailure('Data could not be sent to remote host "%s". Make sure this host can be reached over ssh: %s'
                                               % (self.host, additional))

        # Check for pct errors
        if 'pct: not found' in b_stderr.decode('utf-8', errors='ignore'):
            raise AnsibleError(
                f'pct not found in path of host: {to_text(self.get_option("host"))}')

        return (p.returncode, b_stdout, b_stderr)

    @_ssh_retry
    def _run(self, cmd: list[bytes], in_data: bytes | None, sudoable: bool = True, checkrc: bool = True) -> tuple[int, bytes, bytes]:
        """Wrapper around _bare_run that retries the connection"""
        return self._bare_run(cmd, in_data, sudoable=sudoable, checkrc=checkrc)

    def exec_command(self, cmd: str, in_data: bytes | None = None, sudoable: bool = True) -> tuple[int, bytes, bytes]:
        """ run a command inside the LXC container """
        super(Connection, self).exec_command(cmd, in_data=in_data, sudoable=sudoable)

        self.host = self.get_option('host') or self._play_context.remote_addr

        display.vvv(u"ESTABLISH SSH CONNECTION FOR USER: {0}".format(self.user), host=self.host)

        # Build the pct command to execute inside the container
        pct_cmd = self._build_pct_command(cmd)
        
        ssh_executable = self.get_option('ssh_executable')
        use_tty = self.get_option('use_tty')

        args: tuple[str, ...]
        if not in_data and sudoable and use_tty:
            args = ('-tt', self.host, pct_cmd)
        else:
            args = (self.host, pct_cmd)

        ssh_cmd = self._build_command(ssh_executable, 'ssh', *args)
        (returncode, stdout, stderr) = self._run(ssh_cmd, in_data, sudoable=sudoable)

        return (returncode, stdout, stderr)

    def put_file(self, in_path: str, out_path: str) -> None:
        """ transfer a file from local to remote """
        super(Connection, self).put_file(in_path, out_path)

        self.host = self.get_option('host') or self._play_context.remote_addr
        display.vvv(u"PUT {0} TO {1}".format(in_path, out_path), host=self.host)

        if not os.path.exists(to_bytes(in_path, errors='surrogate_or_strict')):
            raise AnsibleFileNotFound("file or module does not exist: {0}".format(to_native(in_path)))

        try:
            with open(in_path, 'rb') as f:
                data = f.read()
                pct_cmd = self._build_pct_command(
                    ' '.join([
                        self._shell.executable, '-c',
                        self._shell.quote(f'cat > {out_path}')
                    ])
                )
                
                ssh_executable = self.get_option('ssh_executable')
                ssh_cmd = self._build_command(ssh_executable, 'ssh', self.host, pct_cmd)
                returncode, stdout, stderr = self._run(ssh_cmd, data, sudoable=False)
                
            if returncode != 0:
                if 'cat: not found' in stderr.decode('utf-8', errors='ignore'):
                    raise AnsibleError(
                        f'cat not found in path of container: {to_text(self.get_option("vmid"))}')
                raise AnsibleError(
                    f'{to_text(stdout)}\n{to_text(stderr)}')
        except Exception as e:
            raise AnsibleError(
                f'error occurred while putting file from {in_path} to {out_path}!\n{to_text(e)}')

    def fetch_file(self, in_path: str, out_path: str) -> None:
        """ save a remote file to the specified path """
        super(Connection, self).fetch_file(in_path, out_path)

        self.host = self.get_option('host') or self._play_context.remote_addr
        display.vvv(u"FETCH {0} TO {1}".format(in_path, out_path), host=self.host)

        try:
            pct_cmd = self._build_pct_command(
                ' '.join([
                    self._shell.executable, '-c',
                    self._shell.quote(f'cat {in_path}')
                ])
            )
            
            ssh_executable = self.get_option('ssh_executable')
            ssh_cmd = self._build_command(ssh_executable, 'ssh', self.host, pct_cmd)
            returncode, stdout, stderr = self._run(ssh_cmd, None, sudoable=False)
            
            if returncode != 0:
                if 'cat: not found' in stderr.decode('utf-8', errors='ignore'):
                    raise AnsibleError(
                        f'cat not found in path of container: {to_text(self.get_option("vmid"))}')
                raise AnsibleError(
                    f'{to_text(stdout)}\n{to_text(stderr)}')
            
            with open(out_path, 'wb') as f:
                f.write(stdout)
        except Exception as e:
            raise AnsibleError(
                f'error occurred while fetching file from {in_path} to {out_path}!\n{to_text(e)}')

    def reset(self) -> None:
        """ reset the connection """
        run_reset = False
        self.host = self.get_option('host') or self._play_context.remote_addr

        # If we have a persistent ssh connection (ControlPersist), we can ask it to stop listening.
        cmd = self._build_command(self.get_option('ssh_executable'), 'ssh', '-O', 'check', self.host)
        display.vvv(u'sending connection check: %s' % to_text(cmd), host=self.host)
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        status_code = p.wait()
        if status_code != 0:
            display.vvv(u"No connection to reset: %s" % to_text(stderr), host=self.host)
        else:
            run_reset = True

        if run_reset:
            cmd = self._build_command(self.get_option('ssh_executable'), 'ssh', '-O', 'stop', self.host)
            display.vvv(u'sending connection stop: %s' % to_text(cmd), host=self.host)
            p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = p.communicate()
            status_code = p.wait()
            if status_code != 0:
                display.warning(u"Failed to reset connection:%s" % to_text(stderr))

        self.close()

    def close(self) -> None:
        """ terminate the connection """
        self._connected = False

    @property
    def has_tty(self):
        return self._is_tty_requested()

    def _is_tty_requested(self):
        """Check if we require tty"""
        opts = []
        for opt in ('ssh_args', 'ssh_common_args', 'ssh_extra_args'):
            attr = self.get_option(opt)
            if attr is not None:
                opts.extend(self._split_ssh_args(attr))

        args, dummy = self._tty_parser.parse_known_args(opts)

        if args.t:
            return True

        for arg in args.o or []:
            if '=' in arg:
                val = arg.split('=', 1)
            else:
                val = arg.split(maxsplit=1)

            if val[0].lower().strip() == 'requesttty':
                if val[1].lower().strip() in ('yes', 'force'):
                    return True

        return False

    def is_pipelining_enabled(self, wrap_async=False):
        """ override parent method and ensure we don't request a tty """
        if self._is_tty_requested():
            return False
        else:
            return super(Connection, self).is_pipelining_enabled(wrap_async)
