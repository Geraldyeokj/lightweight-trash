const express = require("express");
const scheduledFunctions = require('./scheduledFunctions.js');
const app = express();
app.set("port", process.env.PORT || 7000);
const fs = require("fs");

// Calling CRON jobs.
scheduledFunctions.initScheduledJobs();

app.get('/api/v1/predictions/yhat', (req, res) => {
    console.log('GET - yhat');
    let coord_arr = [];
    const csv_data = fs.readFileSync("./pythonstuff/yhat_current.csv", {encoding: "utf8"});
    const rows = csv_data.split("\n")
    rows.forEach(row => {
      const r = row.split(",")
      coord_arr.push([r[0], r[r.length - 2], r[r.length -1]])
    });
    coord_arr.pop()
    res.send(coord_arr);
})

app.get('/api/v1/predictions/actual', (req, res) => {
    console.log('GET - actual');
    let coord_arr = [];
    const csv_data = fs.readFileSync("./pythonstuff/test_input.csv", {encoding: "utf8"});
    const rows = csv_data.split("\n")
    rows.forEach(row => {
      const r = row.split(",")
      coord_arr.push([r[0], r[r.length - 2], r[r.length -1]])
    });
    // last element is null since there is a trailing newline in yhat_current.csv
    coord_arr.pop()
    res.send(coord_arr);
})

app.listen(app.get("port"), () => {
  console.log("Express server listening on port " + app.get("port"));
});

