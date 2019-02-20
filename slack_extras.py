# -*- coding: utf-8 -*-

import weechat
import re

weechat.register("slack_extras", "bzar", "1.0", "MIT", "Extra stuff for wee-slack", "", "")


def buffer_names():
  infolist = weechat.infolist_get("buffer", "", "")
  if infolist:
    while weechat.infolist_next(infolist):
      name = weechat.infolist_string(infolist, "name")
      yield name
    weechat.infolist_free(infolist)


def slack_buffer_prefix():
  server_aliases_option = weechat.config_get('plugins.var.python.slack.server_aliases')
  server_aliases = weechat.config_string(server_aliases_option) if server_aliases_option else None

  if server_aliases:
    aliases = (alias for server, alias in (
                            item.split(':') for item in server_aliases.split(',')))
    return r'([^.]*\.slack\.com|%s)' % '|'.join(aliases)
  else:
    return r'[^.]*\.slack\.com'

def thread_buffer_names():
  prefix = slack_buffer_prefix()
  thread_buffer_pattern = re.compile(r'%s\.#.*?\.[0-9a-f]{3}' % prefix)
  for name in buffer_names():
    if thread_buffer_pattern.match(name):
      yield name


def dm_buffer_names():
  prefix = slack_buffer_prefix()
  dm_buffer_pattern = re.compile(r'%s.[a-zA-ZåäöÅÄÖ][^&#]*' % prefix)
  for name in buffer_names():
    if dm_buffer_pattern.match(name):
      yield name


def close_buffers_by_names(names):
  for name in names:
    buf = weechat.buffer_search('python', name)
    if buf:
      weechat.prnt('', 'Closing buffer %s' % name)
      weechat.buffer_close(buf)
    else:
      weechat.prnt('', 'Error searching buffer %s' % name)


def close_threads_cb(data, buffer, args):
  weechat.prnt('', 'Closing thread buffers')
  close_buffers_by_names(thread_buffer_names())
  return weechat.WEECHAT_RC_OK


def close_dms_cb(data, buffer, args):
  weechat.prnt('', 'Closing direct message buffers')
  close_buffers_by_names(dm_buffer_names())
  return weechat.WEECHAT_RC_OK


hook = weechat.hook_command(
                "close_threads", "Close all wee-slack thread buffers",
                "", "", "", "close_threads_cb", "")

hook = weechat.hook_command(
                "close_dms", "Close all wee-slack direct message buffers",
                "", "", "", "close_dms_cb", "")
