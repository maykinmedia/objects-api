'use strict';
var fs = require('fs');
var path = require('path');

var argv = require('yargs').argv;
var gulp = require('gulp');
var file = require('gulp-file');
var paths = require('../paths');


/** {string} The components directory. */
var COMPONENTS_DIR = 'components/';


/**
 * Create component task
 * Run using "gulp create-component --name foo [--js --sass --html-include]"
 * Creates files for a new component (BEM block)
 */
gulp.task('create-component', function(cb) {
    if (!argv.name) {
        console.info('Please provide --name argument!');
        return;
    }

    if (!(argv.js || argv.sass || argv.scss || argv.htmlInclude)) {
        console.info('Please provide at least one of the following arguments:');
        console.info('');
        console.info('--js');
        console.info('--sass or --scss');
        console.info('--html-include');
        return;
    }

    var jsComponentsDir = paths.jsSrcDir + COMPONENTS_DIR;
    var sassComponentsDir = paths.sassSrcDir + COMPONENTS_DIR;
    var jsTargetDir = jsComponentsDir + argv.name + '/'
    var sassTargetDir = sassComponentsDir + argv.name + '/';
    var sassAllContents = '';
    var jsIndexContents = '';

    // Generate JS component if --js is passed
    if (argv.js) {
        new file('index.js', 'import \'./' + argv.name + '\';')
            .pipe(gulp.dest(jsTargetDir));

        new file(argv.name + '.js', '')
            .pipe(gulp.dest(jsTargetDir));

        // Update components/index.js
        setTimeout(function() {
            jsIndexContents = getFolders(jsComponentsDir).reduce(function(acc, value) {
                return acc + 'import \'./' + value + '\';\n';
            }, '// THIS IS A GULP GENERATED FILE!!!\n');

            new file('index.js', jsIndexContents)
                .pipe(gulp.dest(jsComponentsDir));
        }, 0);
    }

    // Generate SASS component if --sass or --scss is passed
    if (argv.sass || argv.scss) {
        new file('_all.scss', '@import \'' + argv.name + '\'')
            .pipe(gulp.dest(sassTargetDir));

        new file('_' + argv.name + '.scss', '.' + argv.name + ' {\n}')
            .pipe(gulp.dest(sassTargetDir));

        // Update components/_all.scss
        setTimeout(function() {
            sassAllContents = getFolders(sassComponentsDir).reduce(function(acc, value) {
                return acc + '@import \'' + value + '/all\';\n';
            }, '// THIS IS A GULP GENERATED FILE!!!\n');

            new file('_all.scss', sassAllContents)
                .pipe(gulp.dest(sassComponentsDir));
        }, 0);
    }

    // Creates an HTML file in includes if --html-include is passed
    if (argv.htmlInclude) {
        new file(argv.name + '.html', '')
            .pipe(gulp.dest(paths.htmlIncludesDir + '/' + argv.name))
    }

    cb()
});


/**
 * Returns all the directories in dir
 * @param {string} dir Path to scan
 * @returns {string[]}
 */
function getFolders(dir) {
    return fs.readdirSync(dir)
        .filter(function(file) {
            return fs.statSync(path.join(dir, file)).isDirectory();
        });
}
