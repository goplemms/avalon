def parseAppAndVersion(app_info: str):
    import re
    captures = re.search(r'^([.a-zA-Z]+)\s+([.0-9]+.[0-9]+)$', app_info)

    return (captures.groups(0), captures.groups(1))\
        if captures is not None\
        else None


def determineFailureType(string: str):
    return 'missing_package'\
        if 'package' in string\
        else 'missing_version'


def parseApp(raw_app: str):
    app_info_strings = [x.strip() for x in raw_app.split(':')]

    reason_for_failure = determineFailureType(app_info_strings[0])

    (app_identifier, version) = parseAppAndVersion(app_info_strings[1])\
        if reason_for_failure == 'missing_version'\
        else app_info_strings[1], None

    return {
        'app_identifier': app_identifier,
        'version': version,
        'reason_for_failure': reason_for_failure
    }


def parseApps(command_output: bytes):
    command_output_string = str(command_output, 'UTF-8')
    split_lines = command_output_string.splitlines()

    non_exported_apps = [
        parseApp(raw_app)
        for raw_app in split_lines
        if ':' in raw_app
    ]

    return non_exported_apps


def saveInvalidApps(apps):
    import json
    app_json_string = json.dumps(apps, indent=4)

    with open("desktop-app-list-invalid.json", "w+") as outfile:
        outfile.write(app_json_string)


def saveAppHistory(file='desktop-app-list.json'):
    import subprocess

    command = f'winget export {file} --include-versions'
    winget_export_process = subprocess.Popen(command,
                                             stdout=subprocess.PIPE,
                                             shell=True)

    (output, err) = winget_export_process.communicate(timeout=300)

    non_exported_apps = parseApps(output)
    saveInvalidApps(non_exported_apps)


if __name__ == '__main__':
    saveAppHistory()
