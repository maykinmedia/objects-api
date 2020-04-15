var paths = require('./build/paths');
var webpackConfig = require('./webpack.config.js');

// Add istanbul-instrumenter to webpack configuration
webpackConfig.module.rules.push({
    test: /\.js$/,
    include: __dirname + '/' + paths.jsSrcDir,
    loader: 'istanbul-instrumenter-loader',
    enforce: 'post',

    options: {
        esModules: true
    }
});


// The preprocessor config
var preprocessors = {};
preprocessors[paths.jsSpecEntry] = [
    'webpack'
]


// The main configuration
var configuration = function (config) {
    config.set({
        frameworks: [
            'mocha'
        ],

        files: [
            'node_modules/@babel/polyfill/dist/polyfill.js',
            paths.jsSpecEntry
        ],

        preprocessors: preprocessors,

        webpack: webpackConfig,

        webpackMiddleware: {
            noInfo: true
        },

        reporters: ['coverage', 'junit', 'spec'],

        coverageReporter: {
            dir: 'reports/jstests/',
            reporters: [
                {type: 'html'},
                {type: 'text'},
                {type: 'text-summary'},
            ]
        },

        junitReporter: {
          outputDir: 'reports/jstests/',
          outputFile: 'junit.xml',
          useBrowserName: false,
        },

        // browsers: ['Chromium', 'Firefox', 'PhantomJS'],
        browsers: ['Chromium'],
    });
};

module.exports = configuration;
