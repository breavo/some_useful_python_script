# -*- coding: utf-8 -*-
import urllib

from git import Repo
from gitdb.exc import ODBError
from git.exc import GitCommandError


def git_clone(url_, local_path, master):
    Repo.clone_from(url_, local_path, branch=master)


class GitPackaging(object):

    def __init__(self, local_path):
        self.local_path = local_path
        self.repo = Repo(local_path)

    def git_commit_tracked_files(self, description):
        """
        this func only work to tracked files
        :param description:
        :return:
        """
        files = self.repo.git.diff(None, name_only=True)
        for f in files.split('\n'):
            self.repo.git.add(f)
            self.repo.git.commit('-m', description)

    def git_commit_all(self, description):
        self.repo.git.add('--all')
        self.repo.git.commit('-m', description)

    def git_push(self, local_branch='master', remote_branch='master'):
        """
        this func will not raise exception when push failed
        :param local_branch:
        :param remote_branch:
        :return:
        """
        self.repo.remote().push(refspec='{}:{}'.format(local_branch, remote_branch))

    def git_create_branch(self, l10n_branch):
        self.repo.create_head(l10n_branch)

    def git_del_branch(self, l10n_branch):
        """
        must check out to other branch, then the target branch would be del
        :param l10n_branch:
        :return:
        """
        self.repo.git.branch(d=l10n_branch)

    def git_pull(self):
        remote = self.repo.remotes.origin
        try:
            remote.pull()
        except GitCommandError:
            raise GitCommandError

    def git_force_pull_prepare(self):
        remotes = self.repo.remotes
        for remote in remotes:
            remote.fetch()
        self.repo.git.reset('--hard', 'origin/master')

    def git_inspect_branch(self, l10n_branch):
        try:
            self.repo.rev_parse(l10n_branch)
            return True
        except ODBError:
            print 'there is no such branch named "{}"'.format(l10n_branch)
            return False

    def git_checkout_branch_or_commit(self, branch_name, sha_id=None, force=True):
        current = self.repo.branches[branch_name]
        current.checkout(force=force)
        if sha_id is 'latest' or sha_id is None:
            pass
        else:
            self.repo.git.checkout(sha_id)

    def git_merge_branch(self, other_branch):
        self.repo.git.merge(other_branch)

    def git_clean_untracked_changes(self):
        self.repo.git.clean('-xdf')
        self.repo.git.execute('git checkout .')

    def git_diff(self):
        paths = ''
        self.repo.config_reader()
        ret = self.repo.index.diff(self.repo.remotes.origin.refs.master.commit)
        for path in ret:
            if path.deleted_file is True:
                paths += str(path.a_path) + '\n'
        # print paths
        return paths

    def git_remove_file(self, path):
        try:
            self.repo.git.rm(path)
        except GitCommandError:
            print 'the path {} did not match any files'.format(path)

    def git_fetch_origin(self):
        self.repo.remote().fetch()

    def git_version_rollback(self, commit_id_):
        self.repo.git.reset(commit_id_)

    def git_run_command_directly(self, command):
        """
        run git commands directly, It can be used for debugging
        :param command:
        :return:
        """
        self.repo.git.execute(command)

    def get_l10n_folder_log(self, l10n_path):
        commit_id_ = self.repo.git.log('--pretty=format:"%H" ', '-1', l10n_path)
        return str(commit_id_).strip(' ').strip('"')

    def git_get_conflict_file_report(self, simple=False):
        if simple:
            ret = self.repo.git.diff('--stat').split('diff --cc')
        else:
            ret = self.repo.git.diff().split('diff --cc')
        return ret


def generate_url(url_, username, password):
    username = urllib.quote(username)
    password = urllib.quote(password)
    new_url = (url_[0:8] + '{}:{}@' + url_[8:]).format(username, password)
    # print new_url
    return new_url

if __name__ == '__main__':
    # this is code for test
    local_path_pc = 'F:\\gitClone\\demoPro'
    gp = GitPackaging(local_path_pc)
    url = 'https://adc.github.trendmicro.com/chengjian-liu/demoPro.git'
    branch_list = ['master', 'zh-CN']

    for branch in branch_list:
        gp.git_checkout_branch_or_commit(branch)
        gp.git_version_rollback('b4d50ee8f3d6614b2d9b6c3dcecffd9b635d8c48')
        gp.git_clean_untracked_changes()
    gp.git_checkout_branch_or_commit('master')



