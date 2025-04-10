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
    tempfile_suffix = 'php'
    error_stream = util.STREAM_STDOUT
    line_col_base = (-2, 1)

    def cmd(self):
        command = [
            'php-cs-fixer',
            'fix',
            '${temp_file}',
            '--dry-run',
            '--show-progress=none',
            '--stop-on-violation',
            '--diff-format=udiff' if self.settings.get('version') == 2 else '--diff',
            '--using-cache=no',
            '--no-ansi',
            '-vv'
        ]

        config_file = self.settings.get('config_file') or find_configuration_file(self.view.file_name())
        if config_file:
            command.append(f'--config={config_file}')

        return command
