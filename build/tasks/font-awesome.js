'use strict';
var gulp = require('gulp');
var paths = require('../paths');


/**
 * Font Awesome task
 * Run using "gulp font-awesome"
 * Moves Font Awesome font files to paths.fontDir
 */
function fontAwesome() {
    return gulp.src('node_modules/font-awesome/fonts/*')
        .pipe(gulp.dest(paths.fontsDir));
};

gulp.task('font-awesome', fontAwesome);
exports.fontAwesome = fontAwesome;
