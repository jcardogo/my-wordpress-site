<?php
/**
 * My Theme functions and definitions.
 *
 * @package my-theme
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Sets up theme defaults and registers supported WordPress features.
 */
function my_theme_setup() {
	load_theme_textdomain( 'my-theme', get_template_directory() . '/languages' );

	add_theme_support( 'automatic-feed-links' );
	add_theme_support( 'title-tag' );
	add_theme_support( 'post-thumbnails' );
	add_theme_support(
		'html5',
		array( 'search-form', 'comment-form', 'comment-list', 'gallery', 'caption', 'style', 'script' )
	);

	register_nav_menus(
		array(
			'primary' => esc_html__( 'Primary Menu', 'my-theme' ),
		)
	);
}
add_action( 'after_setup_theme', 'my_theme_setup' );

/**
 * Enqueues theme styles.
 */
function my_theme_scripts() {
	wp_enqueue_style(
		'my-theme-style',
		get_stylesheet_uri(),
		array(),
		wp_get_theme()->get( 'Version' )
	);
}
add_action( 'wp_enqueue_scripts', 'my_theme_scripts' );
