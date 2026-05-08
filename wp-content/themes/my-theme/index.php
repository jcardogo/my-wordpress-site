<?php get_header(); ?>

<section class="hero" aria-labelledby="hero-title">
	<div class="hero__inner">
		<div class="hero__content">
			<p class="hero__eyebrow"><?php bloginfo( 'description' ); ?></p>
			<h1 id="hero-title" class="hero__title"><?php bloginfo( 'name' ); ?></h1>
			<p class="hero__subtitle"><?php esc_html_e( 'A clean, responsive WordPress homepage designed for readable content and clear calls to action.', 'my-theme' ); ?></p>
			<div class="hero__actions">
				<a class="button hero__cta" href="#latest-posts"><?php esc_html_e( 'Explore Posts', 'my-theme' ); ?></a>
				<a class="hero__link" href="<?php echo esc_url( home_url( '/' ) ); ?>"><?php esc_html_e( 'Learn More', 'my-theme' ); ?></a>
			</div>
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
