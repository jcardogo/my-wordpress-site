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

/**
 * Returns the booking API base URL.
 *
 * Use the `my_theme_booking_api_base_url` filter to change this value
 * from a plugin or wp-config bootstrap.
 *
 * @return string
 */
function my_theme_booking_api_base_url() {
	$default_url = 'http://127.0.0.1:5000/api';

	return trailingslashit(
		apply_filters( 'my_theme_booking_api_base_url', $default_url )
	);
}

/**
 * Loads classes from Python API with a short cache.
 *
 * @return array<int, array<string, mixed>>
 */
function my_theme_get_available_classes() {
	$cached = get_transient( 'my_theme_classes_cache' );

	if ( false !== $cached && is_array( $cached ) ) {
		return $cached;
	}

	$response = wp_remote_get(
		my_theme_booking_api_base_url() . 'classes',
		array(
			'timeout' => 10,
		)
	);

	if ( is_wp_error( $response ) ) {
		return array();
	}

	$code = wp_remote_retrieve_response_code( $response );
	$body = wp_remote_retrieve_body( $response );
	$data = json_decode( $body, true );

	if ( 200 !== $code || ! is_array( $data ) || empty( $data['classes'] ) || ! is_array( $data['classes'] ) ) {
		return array();
	}

	set_transient( 'my_theme_classes_cache', $data['classes'], 5 * MINUTE_IN_SECONDS );

	return $data['classes'];
}

/**
 * Handles booking submissions.
 */
function my_theme_handle_booking_submit() {
	if ( ! isset( $_POST['my_theme_booking_nonce'] ) || ! wp_verify_nonce( sanitize_text_field( wp_unslash( $_POST['my_theme_booking_nonce'] ) ), 'my_theme_booking_submit' ) ) {
		wp_die( esc_html__( 'Security validation failed.', 'my-theme' ) );
	}

	$name = isset( $_POST['student_name'] ) ? sanitize_text_field( wp_unslash( $_POST['student_name'] ) ) : '';
	$email = isset( $_POST['student_email'] ) ? sanitize_email( wp_unslash( $_POST['student_email'] ) ) : '';
	$class_id = isset( $_POST['class_id'] ) ? absint( $_POST['class_id'] ) : 0;

	if ( '' === $name || '' === $email || 0 === $class_id ) {
		wp_safe_redirect(
			add_query_arg(
				array(
					'booking_status'  => 'error',
					'booking_message' => rawurlencode( __( 'Please complete all fields.', 'my-theme' ) ),
				),
				home_url( '/' )
			)
		);
		exit;
	}

	$response = wp_remote_post(
		my_theme_booking_api_base_url() . 'bookings',
		array(
			'timeout' => 12,
			'headers' => array(
				'Content-Type' => 'application/json',
			),
			'body'    => wp_json_encode(
				array(
					'student_name'  => $name,
					'student_email' => $email,
					'class_id'      => $class_id,
				)
			),
		)
	);

	if ( is_wp_error( $response ) ) {
		$message = __( 'Unable to reach booking service. Please try again.', 'my-theme' );
		$status = 'error';
	} else {
		$code = wp_remote_retrieve_response_code( $response );
		$body = wp_remote_retrieve_body( $response );
		$data = json_decode( $body, true );

		if ( 201 === $code && is_array( $data ) && ! empty( $data['tracking_id'] ) ) {
			$status = 'success';
			$message = sprintf(
				/* translators: %s: tracking id */
				__( 'Booking created successfully. Tracking ID: %s', 'my-theme' ),
				sanitize_text_field( $data['tracking_id'] )
			);
		} else {
			$status = 'error';
			$message = is_array( $data ) && ! empty( $data['message'] ) ? sanitize_text_field( $data['message'] ) : __( 'Booking failed. Please verify your data and try again.', 'my-theme' );
		}
	}

	wp_safe_redirect(
		add_query_arg(
			array(
				'booking_status'  => $status,
				'booking_message' => rawurlencode( $message ),
			),
			home_url( '/' )
		)
	);
	exit;
}
add_action( 'admin_post_nopriv_my_theme_submit_booking', 'my_theme_handle_booking_submit' );
add_action( 'admin_post_my_theme_submit_booking', 'my_theme_handle_booking_submit' );

/**
 * Handles booking tracking requests.
 */
function my_theme_handle_tracking_submit() {
	if ( ! isset( $_POST['my_theme_tracking_nonce'] ) || ! wp_verify_nonce( sanitize_text_field( wp_unslash( $_POST['my_theme_tracking_nonce'] ) ), 'my_theme_tracking_submit' ) ) {
		wp_die( esc_html__( 'Security validation failed.', 'my-theme' ) );
	}

	$email = isset( $_POST['tracking_email'] ) ? sanitize_email( wp_unslash( $_POST['tracking_email'] ) ) : '';

	if ( '' === $email ) {
		wp_safe_redirect(
			add_query_arg(
				array(
					'tracking_status'  => 'error',
					'tracking_message' => rawurlencode( __( 'Please provide a student email.', 'my-theme' ) ),
				),
				home_url( '/' )
			)
		);
		exit;
	}

	$response = wp_remote_get(
		my_theme_booking_api_base_url() . 'students/' . rawurlencode( $email ) . '/bookings',
		array(
			'timeout' => 10,
		)
	);

	if ( is_wp_error( $response ) ) {
		$message = __( 'Unable to reach tracking service. Please try again.', 'my-theme' );
		$status = 'error';
		$results_token = '';
	} else {
		$code = wp_remote_retrieve_response_code( $response );
		$body = wp_remote_retrieve_body( $response );
		$data = json_decode( $body, true );

		if ( 200 === $code && is_array( $data ) ) {
			$status = 'success';
			$message = __( 'Tracking results loaded.', 'my-theme' );
			$results_token = wp_generate_uuid4();
			set_transient( 'my_theme_tracking_' . $results_token, $data, 2 * MINUTE_IN_SECONDS );
		} else {
			$status = 'error';
			$message = is_array( $data ) && ! empty( $data['message'] ) ? sanitize_text_field( $data['message'] ) : __( 'Tracking failed. Please try again.', 'my-theme' );
			$results_token = '';
		}
	}

	$args = array(
		'tracking_status'  => $status,
		'tracking_message' => rawurlencode( $message ),
	);

	if ( '' !== $results_token ) {
		$args['tracking_token'] = rawurlencode( $results_token );
	}

	wp_safe_redirect( add_query_arg( $args, home_url( '/' ) ) );
	exit;
}
add_action( 'admin_post_nopriv_my_theme_track_student', 'my_theme_handle_tracking_submit' );
add_action( 'admin_post_my_theme_track_student', 'my_theme_handle_tracking_submit' );
