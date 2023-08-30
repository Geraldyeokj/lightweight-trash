const CronJob = require("node-cron");
const { spawn } = require('child_process');
const {createLogger, format, transports} = require("winston");
const path = require('node:path'); 

const winstonLogger = createLogger({
    level: "debug",
    format: format.combine(
        format.timestamp(),
        format.json()
    ),
    transports: [
        new transports.File({ filename: 'combined.log' }),
    ],
});

exports.initScheduledJobs = () => {
    console.log("CRON JOBS ACTIVATED");
    
    const yhatUpdates = CronJob.schedule("*/3 * * * *", () => {
        try{
            console.log('CRON JOB: Updating Yhat | Called every 3 minutes ----------------------------------');
            console.log("current directory:", __dirname)
            winstonLogger.log({
                level: 'verbose',
                message: 'CRON JOB: Updating Yhat | Called every 3 minutes'
            });

            const python = spawn('python3', ["./pythonstuff/yhat_gen_5.py"], {
                cwd: path.resolve(__dirname, "./")
            });

            setTimeout(() => {
                python.kill()
                winstonLogger.log({
                    level: 'warn',
                    message: 'Killed Yhat updating process. Took more than 2 minute 45 seconds.'
                });
                console.log('Killed Yhat updating process. Took more than 2 minute 45 seconds.');
            }, 165*1000, "Yhat child process took too long")

            python.stdout.on('data', (data) => {
                winstonLogger.log({
                    level: 'verbose',
                    message: data.toString()
                });
                console.log('python prints: ', data.toString());
            });
            
            python.stderr.on('data', (data) => {
                winstonLogger.log({
                    level: 'error',
                    message: data.toString()
                });
                console.error('error: ', data.toString());
            });
            
            python.on('error', (error) => {
                winstonLogger.log({
                    level: 'error',
                    message: error
                });
                console.error('error: ', error.message);
            });
            
            python.on('close', (code) => {
                winstonLogger.log({
                    level: 'verbose',
                    message: `child process exited with code  ${code}`
                });
                console.log('child process exited with code ', code);
            });
            console.log("finished generating yhat graph")
        } catch (err) {
            winstonLogger.log({
                level: 'error',
                message: err
            });
            console.warn(`Failed to generate yhat. Error: ${err}`)
        }
    });

    const gasPriceUpdates = CronJob.schedule("15 * * * * *", () => {
        try {
            console.log('CRON JOB: Updating Gas Prices | Called every minute (at the 15 second mark) ------------------');
            console.log("current directory:", __dirname)
            console.log("calling python program from", path.resolve(__dirname, "../../../"))
            winstonLogger.log({
                level: 'verbose',
                message: 'CRON JOB: Updating Gas Prices | Called every minute (at the 15 second mark)'
            });
            
            const process = spawn('python3', ["./pythonstuff/index2.py"], {
                cwd: path.resolve(__dirname, "./")
            });
            setTimeout(() => {
                process.kill()
                winstonLogger.log({
                    level: 'warn',
                    message: 'Killed Gas Price updating process. Took more than 30 seconds.'
                });
                console.log('Killed Gas Price updating process. Took more than 30 seconds.');
            }, 30*1000, "Get gas price took too long")

            process.stdout.on('data', (data) => {
                winstonLogger.log({
                    level: 'verbose',
                    message: data.toString()
                });
                console.log('python prints: ', data.toString());
            });
            
            process.stderr.on('data', (data) => {
                winstonLogger.log({
                    level: 'error',
                    message: data.toString()
                });
                console.error('error: ', data.toString());
            });
            
            process.on('error', (error) => {
                winstonLogger.log({
                    level: 'error',
                    message: error
                });
                console.error('error: ', error.message);
            });
            
            process.on('close', (code) => {
                winstonLogger.log({
                    level: 'verbose',
                    message: `child process exited with code  ${code}`
                });
                console.log('child process exited with code ', code);
            });
            console.log("finished getting gas price")
        } catch (err) {
            winstonLogger.log({
                level: 'error',
                message: err
            });
            console.warn(`Failed to get gas price. Error: ${err}`)
        }
    });

  yhatUpdates.start();
  gasPriceUpdates.start();
}