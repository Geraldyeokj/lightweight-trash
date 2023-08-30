const {createLogger, format, transports} = require("winston");

const logger = createLogger({
    level: "debug",
    format: format.combine(
        format.timestamp(),
        format.json()
    ),
    transports: [
        new transports.File({ filename: 'combined.log' }),
    ],
});

module.exports = logger;
