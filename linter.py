from pathlib import Path

from SublimeLinter.lint import PhpLinter, util


def find_configuration_file(file_name):
    if not file_name:
        return None

    candidates = ['.php-cs-fixer.php', '.php-cs-fixer.dist.php', '.php_cs', '.php_cs.dist']
    for parent in Path(file_name).parents:
        for candidate in candidates:
            configuration_file = parent / candidate
            if configuration_file.is_file():
                return configuration_file

    return None


class PhpCsFixer(PhpLinter):
    """Provides an interface to php-cs-fixer."""

    defaults = {
        'selector': 'embedding.php, source.php, text.html.basic'
    }
    regex = (
        r'^\s+\d+\)\s+.+\s+\((?P<message>.+)\)[^\@]*'
        r'\@\@\s+\-\d+,\d+\s+\+(?P<line>\d+),\d+\s+\@\@'
        r'[^-+]+[-+]?\s+[^\n]*'
    )
    multiline = True
    error_stream = util.STREAM_STDOUT
    line_col_base = (-2, 1)

    def cmd(self):
        if self.settings.get('version') == 2:
            command = ['php-cs-fixer', 'fix', '--dry-run', '--diff-format=udiff']
        else:
            command = ['php-cs-fixer', 'check', '--diff']

        command += [
            # Never ask questions. Without a config file php-cs-fixer asks
            # "Do you want to create the config file?", takes the default
            # without a terminal, and writes .php-cs-fixer.dist.php and
            # .gitignore next to the linted file.
            '--no-interaction',
            '--show-progress=none',
            '--stop-on-violation',
            '--using-cache=no',
            '--no-ansi',
            '-vv'
        ]

        config_file = self.settings.get('config_file') or find_configuration_file(self.view.file_name())
        if config_file:
            command.append(f'--config={config_file}')

        # Read the code from stdin. php-cs-fixer only looks for a config file
        # from the current directory, which is why we pass `--config` above.
        command.append('-')

        return command
