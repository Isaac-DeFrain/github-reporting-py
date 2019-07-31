"""
Repo commit counts report application.

Process a query which supports paging and contains repo commits and iterates
over all the pages. Get all repos owned by user and print the count of commits
on the default branch in each repo. An optional start date cutoff may be
specified.
"""
import sys
import textwrap

import lib


@lib.print_args_on_error
def display(repo):
    """
    Display an easy to read summary of the repo and its commits.
    """
    repo_name = repo['name']
    print(f"Name         : {repo_name}")

    total_commits = 0

    branch = repo.get('defaultBranch')
    if branch:
        branch_name = branch['name']
        history = branch['commits']['history']
        total_commits = history['totalCount']

        if total_commits:
            latest_commit = history['nodes'][0]
            date = latest_commit['committedDate'][:10]
            msg = latest_commit['message']

            print(f"Branch       : {branch_name}")
            print(f"Commits      : {total_commits:,d}")
            print(f"Latest commit:")
            print(f"  {date}")
            print(textwrap.indent(msg, '  '))
        print()
    else:
        # Handle rare cases of an empty repo.
        print(f"No branch data")

    return total_commits


def main(args):
    """
    Main command-line function.
    """
    if not args or set(args).intersection({'-h', '--help'}):
        print(f"Usage: {__file__} owner OWNER [start START_DATE]")
        print(f"START_DATE: Count commits on or after this date, in YYYY-MM-DD format.")
        sys.exit(1)

    path = 'queries/repos/repos_and_commit_counts.gql'
    variables = lib.process_variables(args)

    grand_total = 0
    first_iteration = True

    while True:
        resp_data = lib.query_by_filename(path, variables)
        repositories = resp_data['repositoryOwner']['repositories']

        if first_iteration:
            print(f"Total count: {repositories['totalCount']}")
            first_iteration = False

        for repo in repositories['nodes']:
            grand_total += display(repo)

        repo_page_info = repositories['pageInfo']
        if repo_page_info['hasNextPage']:
            variables['cursor'] = repo_page_info['endCursor']
        else:
            break

    print(f"Total commits across repos: {grand_total}")

if __name__ == '__main__':
    main(sys.argv[1:])
