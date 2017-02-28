#!/usr/bin/env node

// Proxies backend requests to the specified cockroach node.

var express = require('express');
var app      = express();
var httpProxy = require('http-proxy');
var apiProxy = httpProxy.createProxyServer({secure:false});

var argv = require('yargs')
  .usage('Usage: $0 <remote-cockroach-ui-url> [options]')
  .demand(1)
  .default('port', 3000, 'The port to run this proxy server on')
  .example(`$0 https://myroach:8080`, 'Serve API data requests from https://myroach:8080')
  .help('h')
  .alias('h', 'help')
  .alias('p', 'port')
  .argv;

var remote = argv._[0],
  port = argv.port;

console.log(`Proxying requests to ${remote}. UI visible at http://localhost:${port}`);

app.all("/_admin/v1*", function(req, res) {
  apiProxy.web(req, res, {target: remote});
});

app.all("/_status*", function(req, res) {
  apiProxy.web(req, res, {target: remote});
});

app.all("/ts/*", function(req, res) {
  apiProxy.web(req, res, {target: remote});
});

app.use(express.static('.'));

app.listen(port);

// Catch-all error handler
apiProxy.on('error', function (err, req, res) {
  console.error(err);
  res.status(500);
  res.send({ error: err });
});
