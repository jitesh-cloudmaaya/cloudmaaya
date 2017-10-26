// USAGE: gulp
// USAGE: NODE_ENV=prod gulp

var cache = require('gulp-cache'),
	concat = require('gulp-concat'), // https://www.npmjs.com/package/gulp-concat
	cssComb = require('gulp-csscomb'), // .csscomb
	cssNano = require('gulp-cssnano'),
	del = require('del')
	gulp = require('gulp'),
	gulpIf = require('gulp-if'),
	gulpRename = require('gulp-rename'),
	gulpReplace = require('gulp-replace'),
	gulpUtil = require('gulp-util'),
	htmlLint = require('gulp-htmllint'), // .htmllintrc -- https://github.com/htmllint/htmllint/wiki/Options
	htmlMin = require('gulp-htmlmin'),
	jshint = require('gulp-jshint'), // .jshintignore
	notify = require('gulp-notify'),
	nunjucksRender = require('gulp-nunjucks-render'),
	plumber = require('gulp-plumber'),
	runSequence = require('run-sequence'),
	smushIt = require('gulp-smushit'), // Using SmushIt over ImageMin as ImageMin breaks on Nginx -- http://resmush.it/api
	sourcemaps = require('gulp-sourcemaps'),
	uglify = require('gulp-uglify'); // https://www.npmjs.com/package/gulp-uglify

var env = process.env.NODE_ENV || 'dev',
	distDir = 'dist/',
	srcDir = 'src/';

var config = {
	'dev': {
		'bugSnagEnvironment': 'development',
		'gaTrackingId': 'UA-91990207-2'
	},
	'stage': {
		'bugSnagEnvironment': 'development',
		'gaTrackingId': 'UA-91990207-2'
	},
	'prod': {
		'bugSnagEnvironment': 'production',
		'gaTrackingId': 'UA-91990207-1'
	}
};

// Datestamp for cache busting
var getStamp = function() {
	var date = new Date();
	
	var year = date.getFullYear().toString();
	var month = ('0' + (date.getMonth() + 1)).slice(-2);
	var day = ('0' + date.getDate()).slice(-2);
	var seconds = date.getSeconds().toString();
	
	var fullDate = year + month + day + seconds;
	
	return fullDate;
};

gulp.task('build', ['clean'], function(callback) {
	runSequence('properties',
		[
			'css', 'css-quiz', 
			'html', 
			'img', 
			'js-looks',
			'robots'
		],
		callback);
});

gulp.task('clean', function() {
	return del(distDir + '/**/*'); // Does not delete .files
});

gulp.task('comb', function() {
	return gulp.src(srcDir + 'css/**/*.css')
		.pipe(cssComb('./.csscomb.json'))
		.pipe(gulp.dest(srcDir + 'css'));
});

gulp.task('css', function() {
	return gulp.src(srcDir + 'css/**/*.css')
		.pipe(customPlumber('Error Running CSS'))
		.pipe(concat('index.min.css'))
		.pipe(cssNano())
		.pipe(gulp.dest(distDir + 'css'));
});

gulp.task('default', function(callback) {
	
	if (env === 'dev') {
		
		runSequence('clean',
			'properties',
			[
				'css', 'css-quiz', 
				'html', 
				'js-looks',
				'misc', 'robots'
			],
			['comb', 'img', 'js-lint'],
			'watch', // Don't do this on Jenkins
			callback);
		
	} else {
		
		runSequence('clean',
			'properties',
			[
				'css', 'css-quiz', 
				'html', 
				'js-looks',
				'misc', 'robots'
			],
			['comb', 'img', 'js-lint'],
			callback);
	}
});

gulp.task('html', function() {
	return gulp.src(srcDir + 'html/pages/**/*.html')
		.pipe(customPlumber('Error Running HTML'))
		.pipe(nunjucksRender({
			data: {
				bugSnagEnvironment: config[env]['bugSnagEnvironment'],
				
				gaTrackingId: config[env]['gaTrackingId']
			},
			path: [srcDir + 'html/templates']
		}))
        .pipe(htmlMin({
	        collapseWhitespace: true,
	        removeComments: true
	    }))
	    
		// Cache busting
		.pipe(gulpReplace(/index.min.css\?([0-9]*)/g, 'index.min.css?' + getStamp()))
		.pipe(gulpReplace(/index.min.js\?([0-9]*)/g, 'index.min.js?' + getStamp()))
		
		.pipe(gulp.dest(distDir));
});

gulp.task('html-lint', function() {
    return gulp.src(srcDir + 'html/pages/**/*.html')
        .pipe(htmlLint({}, htmlLintReporter));
});

function htmlLintReporter(filepath, issues) {	
    if (issues.length > 0) {
        issues.forEach(function (issue) {
            gulpUtil.log(gulpUtil.colors.cyan('[gulp-htmlLint] ') + gulpUtil.colors.white(filepath + ' [' + issue.line + ',' + issue.column + ']: ') + gulpUtil.colors.red('(' + issue.code + ') ' + issue.msg));
        });
 
        process.exitCode = 1;
    }
}

gulp.task('img', function(){
    return gulp.src(srcDir + 'img/**/*')
    	.pipe(customPlumber('Error Running Img'))
       .pipe(gulp.dest(distDir + 'img'));
});

gulp.task('js-looks', function() {
	
	return gulp.src([
			srcDir + 'js/lib/Device.js',
			srcDir + 'js/lib/js.cookie.js',
			srcDir + 'js/lib/moment.js',

			srcDir + 'js/lib/BH.js',
			srcDir + 'js/lib/System.js',
			srcDir + 'js/lib/jquery.mobile.custom.min.js', // Contains only swipeleft, etc. events
			srcDir + 'js/lib/underscore-min.js',
			srcDir + 'js/lib/Util.js',
			
			srcDir + 'js/shared/Constants.js',
			srcDir + 'js/shared/GoogleAnalytics.js',
			srcDir + 'js/shared/GlobalEvents.js', // Required by EcommerceService.js
			srcDir + 'js/shared/Globals.js', // Required by EcommerceService.js
			srcDir + 'js/shared/Hash.js',
			srcDir + 'js/shared/Modal.js',

			srcDir + 'js/shared/inputs/BaseCompositeInput.js',
			srcDir + 'js/shared/inputs/Validation.js',
			srcDir + 'js/shared/inputs/Button.js',
			srcDir + 'js/shared/inputs/SelectInput.js',
			srcDir + 'js/shared/inputs/TextAreaInput.js',

			srcDir + 'js/properties.js',

			srcDir + 'js/services/EcommerceService.js', // This needs to be before any app includes
			srcDir + 'js/services/BaseService.js',
			srcDir + 'js/services/SocialService.js',
			srcDir + 'js/services/StylingService.js',
			srcDir + 'js/services/TrackingService.js',

			srcDir + 'js/app/shared/CommentModal.js',
			srcDir + 'js/app/shared/DescripCommenting.js',
			srcDir + 'js/app/shared/ErrorModal.js',
			srcDir + 'js/app/shared/Heart.js',
			srcDir + 'js/app/shared/ImageView.js',
			srcDir + 'js/app/shared/LooksHeader.js',
			srcDir + 'js/app/shared/ProductUtil.js',
			srcDir + 'js/app/shared/Rate.js',

			srcDir + 'js/app/Looks/LooksUtil.js',
			srcDir + 'js/app/Looks/LookProduct.js',
			srcDir + 'js/app/Looks/Intro.js',
			srcDir + 'js/app/Looks/Looks.js',
			
			srcDir + 'js/app/Looks/Index.js'
		])
		.pipe(customPlumber('Error Running JS'))
		.pipe(gulpIf(env == 'dev', sourcemaps.init()))
 		.pipe(concat('looks.min.js'))
		.pipe(uglify())
		.pipe(gulpIf(env == 'dev', sourcemaps.write('maps')))
		.pipe(gulp.dest(distDir + 'js'));
});

gulp.task('js-lint', function() {
	return gulp.src(srcDir + 'js/**/*.js')
	
		// http://jshint.com/docs/options/
		.pipe(jshint({
			evil: true,
			globals: {
			    'BH': true,
			    'window': false,
			    '$': false
			},
			loopfunc: true,
			strict: true,
            sub: true
		}))
		.pipe(jshint.reporter('jshint-stylish', { verbose: true })); // Running with verbose will give the warning number in case you need to suppress it.
});

gulp.task('misc', function() {

	gulp.src(srcDir + '/js/lib/bugsnag-3.min.js')
		.pipe(gulp.dest(distDir + 'js'));

	gulp.src(srcDir + 'sitemap.xml')
		.pipe(gulp.dest(distDir));
});

gulp.task('properties', function() {

	return gulp.src(srcDir + 'properties/' + env + '.js')
				.pipe(gulpRename('properties.js'))
				.pipe(gulp.dest(srcDir + 'js'));
});

gulp.task('robots', function() {
	
	var fileName = '';

	if (env === 'prod') {
		fileName = 'prod';
	} else {
		fileName = 'stage';
	}
	
	return gulp.src(srcDir + 'robots/' + fileName + '.txt')
				.pipe(gulpRename('robots.txt'))
				.pipe(gulp.dest(distDir));
});

gulp.task('watch', function() {
	gulp.watch(srcDir + 'css/**/*.css', ['css', 'css-quiz']);

	gulp.watch(srcDir + '**/*.html', ['html']).on('error', errorHandler);

	gulp.watch(srcDir + 'img/**/*', ['img']);

	gulp.watch(srcDir + 'js/app/Looks/*.js', ['js-looks']);
});

function customPlumber(errorTitle) {
	return plumber({
		errorHandler: notify.onError({
			message: 'ERROR: <%= error.message %>',
			sound: 'Submarine', // Basso, Blow, Bottle, Frog, Funk, Glass, Hero, Morse, Ping, Pop, Purr, Sosumi, Submarine, Tink
			title: errorTitle || 'Error Running Gulp'
		})
	});
}

function errorHandler(error) {
	console.log(error.toString());
	this.emit('end'); // Ends the current pipe so Gulp watch doesn't break
}
