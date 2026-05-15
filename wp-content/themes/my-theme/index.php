<?php get_header(); ?>

<section class="hero" aria-labelledby="hero-title">
	<div class="hero__inner">
		<div class="hero__content">
			<p class="hero__eyebrow"><?php bloginfo( 'description' ); ?></p>
			<h1 id="hero-title" class="hero__title"><?php bloginfo( 'name' ); ?></h1>
			<p class="hero__subtitle"><?php esc_html_e( 'A clean, responsive WordPress homepage designed for readable content and clear calls to action.', 'my-theme' ); ?></p>
			<div class="hero__actions">
				<a class="button hero__cta" href="#latest-posts"><?php esc_html_e( 'Explore Posts', 'my-theme' ); ?></a>
				<a class="button hero__cta" href="#student-booking"><?php esc_html_e( 'Book a Class', 'my-theme' ); ?></a>
				<a class="hero__link" href="<?php echo esc_url( home_url( '/' ) ); ?>"><?php esc_html_e( 'Learn More', 'my-theme' ); ?></a>
			</div>
		</div>
	</div>
</section>

<?php
$classes = function_exists( 'my_theme_get_available_classes' ) ? my_theme_get_available_classes() : array();

$booking_status  = isset( $_GET['booking_status'] ) ? sanitize_text_field( wp_unslash( $_GET['booking_status'] ) ) : '';
$booking_message = isset( $_GET['booking_message'] ) ? sanitize_text_field( wp_unslash( $_GET['booking_message'] ) ) : '';

$tracking_status  = isset( $_GET['tracking_status'] ) ? sanitize_text_field( wp_unslash( $_GET['tracking_status'] ) ) : '';
$tracking_message = isset( $_GET['tracking_message'] ) ? sanitize_text_field( wp_unslash( $_GET['tracking_message'] ) ) : '';
$tracking_token   = isset( $_GET['tracking_token'] ) ? sanitize_text_field( wp_unslash( $_GET['tracking_token'] ) ) : '';
$tracking_results = array();

if ( '' !== $tracking_token ) {
	$tracking_results = get_transient( 'my_theme_tracking_' . $tracking_token );
	delete_transient( 'my_theme_tracking_' . $tracking_token );
}
?>

<section id="student-booking" class="booking-section" aria-labelledby="student-booking-title">
	<div class="booking-section__inner">
		<div class="booking-card">
			<h2 id="student-booking-title"><?php esc_html_e( 'Student Class Booking', 'my-theme' ); ?></h2>
			<p><?php esc_html_e( 'Register a student in a class and generate a tracking ID.', 'my-theme' ); ?></p>

			<?php if ( '' !== $booking_message ) : ?>
				<p class="notice <?php echo 'success' === $booking_status ? 'notice--success' : 'notice--error'; ?>">
					<?php echo esc_html( rawurldecode( $booking_message ) ); ?>
				</p>
			<?php endif; ?>

			<form action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>" method="post" class="booking-form">
				<input type="hidden" name="action" value="my_theme_submit_booking" />
				<?php wp_nonce_field( 'my_theme_booking_submit', 'my_theme_booking_nonce' ); ?>

				<label for="student_name"><?php esc_html_e( 'Student Name', 'my-theme' ); ?></label>
				<input id="student_name" name="student_name" type="text" required />

				<label for="student_email"><?php esc_html_e( 'Student Email', 'my-theme' ); ?></label>
				<input id="student_email" name="student_email" type="email" required />

				<label for="class_id"><?php esc_html_e( 'Class Offered', 'my-theme' ); ?></label>
				<select id="class_id" name="class_id" required>
					<option value=""><?php esc_html_e( 'Select a class', 'my-theme' ); ?></option>
					<?php foreach ( $classes as $class_item ) : ?>
						<option value="<?php echo esc_attr( isset( $class_item['id'] ) ? $class_item['id'] : '' ); ?>">
							<?php
							echo esc_html(
								sprintf(
									'%s (%s)',
									isset( $class_item['name'] ) ? $class_item['name'] : __( 'Unnamed class', 'my-theme' ),
									isset( $class_item['code'] ) ? $class_item['code'] : __( 'no code', 'my-theme' )
								)
							);
							?>
						</option>
					<?php endforeach; ?>
				</select>

				<button type="submit"><?php esc_html_e( 'Create Booking', 'my-theme' ); ?></button>
			</form>
		</div>

		<div class="booking-card">
			<h2><?php esc_html_e( 'Track Student Bookings', 'my-theme' ); ?></h2>
			<p><?php esc_html_e( 'Enter a student email to list every class booking and status.', 'my-theme' ); ?></p>

			<?php if ( '' !== $tracking_message ) : ?>
				<p class="notice <?php echo 'success' === $tracking_status ? 'notice--success' : 'notice--error'; ?>">
					<?php echo esc_html( rawurldecode( $tracking_message ) ); ?>
				</p>
			<?php endif; ?>

			<form action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>" method="post" class="booking-form">
				<input type="hidden" name="action" value="my_theme_track_student" />
				<?php wp_nonce_field( 'my_theme_tracking_submit', 'my_theme_tracking_nonce' ); ?>

				<label for="tracking_email"><?php esc_html_e( 'Student Email', 'my-theme' ); ?></label>
				<input id="tracking_email" name="tracking_email" type="email" required />

				<button type="submit"><?php esc_html_e( 'Track Bookings', 'my-theme' ); ?></button>
			</form>

			<?php if ( is_array( $tracking_results ) && ! empty( $tracking_results['bookings'] ) && is_array( $tracking_results['bookings'] ) ) : ?>
				<div class="tracking-results">
					<h3><?php esc_html_e( 'Booking History', 'my-theme' ); ?></h3>
					<ul>
						<?php foreach ( $tracking_results['bookings'] as $booking ) : ?>
							<li>
								<strong><?php echo esc_html( isset( $booking['class_name'] ) ? $booking['class_name'] : __( 'Unknown class', 'my-theme' ) ); ?></strong>
								<span><?php echo esc_html( isset( $booking['status'] ) ? strtoupper( $booking['status'] ) : __( 'UNKNOWN', 'my-theme' ) ); ?></span>
								<small><?php echo esc_html( isset( $booking['tracking_id'] ) ? $booking['tracking_id'] : '' ); ?></small>
							</li>
						<?php endforeach; ?>
					</ul>
				</div>
			<?php endif; ?>
		</div>
	</div>
</section>

<main id="latest-posts" class="site-main">
	<?php if ( have_posts() ) : ?>
		<div class="posts-grid">
			<?php while ( have_posts() ) : the_post(); ?>
				<article id="post-<?php the_ID(); ?>" <?php post_class( 'card' ); ?>>
					<?php if ( has_post_thumbnail() ) : ?>
						<a class="card__thumbnail" href="<?php the_permalink(); ?>" tabindex="-1" aria-hidden="true">
							<?php the_post_thumbnail( 'medium_large' ); ?>
						</a>
					<?php endif; ?>
					<header class="entry-header">
						<?php the_title( sprintf( '<h2 class="entry-title"><a href="%s">', esc_url( get_permalink() ) ), '</a></h2>' ); ?>
						<div class="entry-meta">
							<time datetime="<?php echo esc_attr( get_the_date( 'c' ) ); ?>"><?php echo esc_html( get_the_date() ); ?></time>
						</div>
					</header>
					<div class="entry-summary">
						<?php the_excerpt(); ?>
					</div>
					<footer class="entry-footer">
						<a class="read-more" href="<?php the_permalink(); ?>"><?php esc_html_e( 'Read more', 'my-theme' ); ?></a>
					</footer>
				</article>
			<?php endwhile; ?>
		</div>
	<?php else : ?>
		<section class="no-results">
			<h2><?php esc_html_e( 'No posts yet', 'my-theme' ); ?></h2>
			<p><?php esc_html_e( 'Publish your first post to populate the homepage grid.', 'my-theme' ); ?></p>
		</section>
	<?php endif; ?>
</main>

<?php get_footer(); ?>
