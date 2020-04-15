const gulp = require('gulp');
const paths = require('../paths');
const {js} = require('./js');
const {lint} = require('./lint');
const {scss} = require('./scss');


/**
 * Watch task
 * Run using "gulp watch"
 * Runs "watch-js" and "watch-sass" tasks
 */
const watch = gulp.parallel(watchJS, watchSCSS);


/**
 * Watch-js task
 * Run using "gulp watch-js"
 * Runs "js" and "lint" tasks instantly and when any file in paths.jsSrc changes
 */
function watchJS() {
    js();
    gulp.watch([paths.jsSrc, paths.jsSpec], gulp.parallel(js, lint));
}

/**
 * Watch-sass task
 * Run using "gulp watch-scss"
 * Runs "sass" task instantly and when any file in paths.sassSrc changes
 */
function watchSCSS() {
    scss()
    gulp.watch(paths.sassSrc, scss);
}



exports.watch = watch;
gulp.task('watch', watch);


exports.watchJS = watchJS;
gulp.task('watch-js', watchJS);


exports.watchSCSS = watchSCSS;
gulp.task('watch-scss', watchSCSS);
