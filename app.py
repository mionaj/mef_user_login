import http.server, os
import urllib, uuid


class Handler(http.server.BaseHTTPRequestHandler):
    def _set_headers(self, type, response_code=200):
        self.send_response(response_code)
        self.send_header('Content-type', type)
        self.end_headers()

    def import_passwd(self):
        passwd = []

        with open("passwd", "r") as p:
            for line in p:
                fields = line.strip().split(':')

                account_data = {"username": fields[0],
                                "gecos": fields[1],
                                "password": fields[2]}

                passwd += [account_data]

        return passwd

    def log_action(self, time, username, ip, action):
        with open("history.log", "a") as h:
            h.write('{0} {1} {2} {3}\n'.format(time, username, ip, action))
        return True

    def generate_history_table(self, username):
        html = ''
        with open("history.log", "r") as h:
            for line in h:
                fields = line.strip().split(' ')
                if fields[2] == username:
                    html += '<tr>'
                    html += '<td align="right">{0}</td>'.format(' '.join(fields[:2]))
                    html += '<td align="center">{0}</td>'.format(fields[2])
                    html += '<td align="center">{0}</td>'.format(fields[3])
                    html += '<td align="center">{0}</td>'.format(fields[4])
                    html += '</tr>'

        return html

    def respond_login_bad(self):
        self.appresponse_raw_file("login_bad.html")
        return True

    def appresponse_history(self):
        if "Cookie" in self.headers:
            session_id = self.headers["Cookie"].split('=')[1]
            with open("sessions/" + session_id, "r") as s:
                account_username = s.read()

            html = '''<!DOCTYPE html>
                            <html>
                              <head>
                                <meta charset="UTF-8">
                                <meta name="description" content="Lekcija 2">
                                <meta name="keywords" content="HTML,CSS,XML,JavaScript">
                                <meta name="author" content="Milan Popovic">
                                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                                <title>Lekcija 2</title>
                                <link rel="stylesheet" href="static/app.css">
                                <script src="static/app.js"></script>
                              </head>
                              <body>
                            '''
            html += '<p><a href="/">Home</a></p>'
            html += '<table border="1" align="center" cellpadding="2" cellspacing="0" nowrap>'
            html += '<tr><th align="center">Time</th><th align="center">Username</th><th align="center">IP address</th><th align="center">Action</th></tr>'

            html += self.generate_history_table(account_username)
            html += '</table>'
            html += '</body></html>'

            self.send_response(200)
            self.send_header('Content-type', "text/html")
            self.end_headers()
            self.wfile.write(str.encode(str(html)))
        else:
            self.send_response(303)
            self.send_header('Location', '/login')
            self.end_headers()
        return True

    def appresponse_raw_file(self, file, response_code=200, content_type="text/html"):
        self.send_response(response_code)
        self.send_header('Content-type', content_type)
        self.end_headers()
        html = open(file, 'r').read()
        self.wfile.write(str.encode(str(html)))
        return

    def extension_to_content_type(self, extension):
        if extension in ["html", "htm"]:
            return "text/html"
        elif extension in ["txt", "js", "py", "php"]:
            return "text/plain"
        elif extension in ["css"]:
            return "text/css"
        elif extension in ["ico", "jpg", "jpeg", "png", "gif"]:
            return "image/x-icon"
        else:
            return False

    def do_GET(self):
        rpath = self.path[1:]
        approute = self.path.split("/")[-1]
        extension = approute.split(".")[-1]

        if approute == "history":
            self.appresponse_history()
        elif approute == "":
            self.appresponse_raw_file("index.html")
        elif approute == "login":
            self.appresponse_raw_file("login.html")
        elif self.path.split("/")[1] == "static":
            if os.access(rpath, os.R_OK) and not os.path.isdir(rpath):
                self.appresponse_raw_file(rpath, content_type=self.extension_to_content_type(extension))
            else:
                self.appresponse_raw_file("error404.html", response_code=404)
        else:
            self.appresponse_raw_file("error404.html", response_code=404)

        return

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        content = self.rfile.read(content_length).decode("utf-8")
        account = urllib.parse.parse_qs(content)

        account_authorized = False
        account_authenticated = False

        try:
            account_username = account['username'][0]
        except KeyError:
            self.respond_login_bad()
            return False

        try:
            account_password = account['password'][0]
        except KeyError:
            self.respond_login_bad()
            return False

        passwd = self.import_passwd()

        for acc in passwd:
            if acc['username'] == account_username:
                account_authorized = True
                if acc['password'] == account_password:
                    account_authenticated = True
                break

        if account_authorized and account_authenticated:
            self.log_action(self.log_date_time_string(), account_username, self.client_address[0], "session_start")

            session_id = str(uuid.uuid1())

            with open('sessions/' + session_id, "w") as s:
                s.write(account_username)

            self.send_response(303)
            self.send_header('Location', '/history')
            self.send_header('Set-Cookie', 'session=' + session_id)
            self.end_headers()
            return True
        elif account_authorized and not account_authenticated:
            self.log_action(self.log_date_time_string(), account_username, self.client_address[0], "bad_password")
            self.respond_login_bad()
            return False

        else:
            self.respond_login_bad()
            return False


try:
    port = int(os.environ["PORT"])
    httpd = http.server.HTTPServer(('0.0.0.0', port), Handler)
    print("Server startovan...port: " + str(port))
    httpd.serve_forever()
except:
    print("Server stopiran")
