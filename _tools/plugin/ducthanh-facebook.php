<?php
/**
 * Plugin Name: Đức Thành – Đăng Facebook
 * Description: Tự động đăng bài ảnh (ảnh đại diện + nội dung) lên Fanpage khi xuất bản sản phẩm hoặc bài viết.
 * Version: 1.2.2
 * Author: Đức Thành
 * Requires PHP: 7.4
 */
if ( ! defined( 'ABSPATH' ) ) { exit; }

define( 'DTFB_API', 'https://graph.facebook.com/v26.0/' );
define( 'DTFB_TYPES', array( 'product', 'post' ) );

/* ---------- Trang cài đặt ---------- */
add_action( 'admin_menu', function () {
	add_options_page( 'Đăng Facebook', 'Đăng Facebook', 'manage_options', 'dtfb', 'dtfb_settings_page' );
} );

function dtfb_settings_page() {
	if ( ! current_user_can( 'manage_options' ) ) { return; }
	$msg = '';
	if ( isset( $_POST['dtfb_save'] ) && check_admin_referer( 'dtfb_save' ) ) {
		update_option( 'dtfb_page_id', sanitize_text_field( wp_unslash( $_POST['dtfb_page_id'] ?? '' ) ), false );
		$tok = trim( sanitize_text_field( wp_unslash( $_POST['dtfb_token'] ?? '' ) ) );
		if ( $tok !== '' ) { update_option( 'dtfb_token', $tok, false ); }
		update_option( 'dtfb_enabled', isset( $_POST['dtfb_enabled'] ) ? '1' : '0', false );
		update_option( 'dtfb_add_link', isset( $_POST['dtfb_add_link'] ) ? '1' : '0', false );
		update_option( 'dtfb_hotline', sanitize_text_field( wp_unslash( $_POST['dtfb_hotline'] ?? '' ) ), false );
		$msg = 'Đã lưu cài đặt.';
	}
	if ( isset( $_POST['dtfb_test'] ) && check_admin_referer( 'dtfb_save' ) ) {
		$r = dtfb_api_get( get_option( 'dtfb_page_id' ), array( 'fields' => 'name' ) );
		$msg = is_wp_error( $r ) ? 'Lỗi kết nối: ' . $r->get_error_message() : 'Kết nối tốt với Fanpage: ' . ( $r['name'] ?? '?' );
	}
	$has_token = get_option( 'dtfb_token' ) ? true : false;
	?>
	<div class="wrap">
		<h1>Đức Thành – Đăng Facebook</h1>
		<?php if ( $msg ) : ?><div class="notice notice-info"><p><?php echo esc_html( $msg ); ?></p></div><?php endif; ?>
		<form method="post">
			<?php wp_nonce_field( 'dtfb_save' ); ?>
			<table class="form-table">
				<tr><th>Bật tự động đăng</th><td><label><input type="checkbox" name="dtfb_enabled" value="1" <?php checked( get_option( 'dtfb_enabled', '1' ), '1' ); ?>> Đăng lên Fanpage khi xuất bản sản phẩm / bài viết</label></td></tr>
				<tr><th>Gắn link bài web</th><td><label><input type="checkbox" name="dtfb_add_link" value="1" <?php checked( get_option( 'dtfb_add_link', '0' ), '1' ); ?>> Gắn link bài web vào bài Facebook (Facebook giới hạn ~2 bài có link/tháng – nên để TẮT)</label></td></tr>
				<tr><th>Hotline trên Facebook</th><td><input type="text" class="regular-text" name="dtfb_hotline" value="<?php echo esc_attr( get_option( 'dtfb_hotline', '0971 024 840' ) ); ?>"></td></tr>
				<tr><th>ID Fanpage</th><td><input type="text" class="regular-text" name="dtfb_page_id" value="<?php echo esc_attr( get_option( 'dtfb_page_id', '' ) ); ?>"></td></tr>
				<tr><th>Mã truy cập Fanpage</th><td><input type="password" class="large-text" name="dtfb_token" value="" autocomplete="off" placeholder="<?php echo $has_token ? 'Đã lưu – để trống nếu không đổi' : 'Dán mã EAA… của Fanpage'; ?>">
				<p class="description">Mã được lưu trên máy chủ web, không hiển thị lại.</p></td></tr>
			</table>
			<p><button class="button button-primary" name="dtfb_save" value="1">Lưu</button>
			<button class="button" name="dtfb_test" value="1">Kiểm tra kết nối</button></p>
		</form>
		<?php
		$q = get_posts( array( 'post_type' => DTFB_TYPES, 'posts_per_page' => 100, 'meta_key' => 'dtfb_status', 'meta_compare' => 'EXISTS', 'orderby' => 'modified' ) );
		if ( $q ) {
			echo '<h2>Trạng thái đăng Facebook</h2><table class="widefat striped"><tbody>';
			foreach ( $q as $x ) { echo '<tr><td>' . esc_html( get_the_title( $x ) ) . '</td><td>' . esc_html( get_post_meta( $x->ID, 'dtfb_status', true ) ) . '</td></tr>'; }
			echo '</tbody></table>';
		}
		$last = get_option( 'dtfb_last_log' ); if ( $last ) : ?>
			<h2>Lần đăng gần nhất</h2><p><?php echo esc_html( $last ); ?></p>
		<?php endif; ?>
	</div>
	<?php
}

/* ---------- Gọi API ---------- */
function dtfb_api_get( $path, $args ) {
	$tok = get_option( 'dtfb_token' );
	if ( ! $tok || ! $path ) { return new WP_Error( 'dtfb', 'Chưa có ID Fanpage hoặc mã truy cập.' ); }
	$args['access_token'] = $tok;
	$res = wp_remote_get( DTFB_API . rawurlencode( $path ) . '?' . http_build_query( $args ), array( 'timeout' => 20 ) );
	return dtfb_parse( $res );
}
function dtfb_api_post( $path, $args ) {
	$tok = get_option( 'dtfb_token' );
	if ( ! $tok ) { return new WP_Error( 'dtfb', 'Chưa có mã truy cập.' ); }
	$args['access_token'] = $tok;
	$res = wp_remote_post( DTFB_API . $path, array( 'timeout' => 45, 'body' => $args ) );
	return dtfb_parse( $res );
}
function dtfb_parse( $res ) {
	if ( is_wp_error( $res ) ) { return $res; }
	$j = json_decode( wp_remote_retrieve_body( $res ), true );
	if ( isset( $j['error'] ) ) { return new WP_Error( 'dtfb', ( $j['error']['message'] ?? 'Lỗi' ) . ' (mã ' . ( $j['error']['code'] ?? '?' ) . ')' ); }
	return is_array( $j ) ? $j : new WP_Error( 'dtfb', 'Phản hồi không hợp lệ.' );
}

/* ---------- Nội dung đăng ---------- */
function dtfb_message( $post ) {
	$m = trim( (string) get_post_meta( $post->ID, 'dtfb_message', true ) );
	if ( $m === '' ) {
		$ex = $post->post_excerpt ? $post->post_excerpt : wp_trim_words( $post->post_content, 45, '…' );
		$ex = trim( html_entity_decode( wp_strip_all_tags( $ex ), ENT_QUOTES, 'UTF-8' ) );
		$m  = html_entity_decode( get_the_title( $post ), ENT_QUOTES, 'UTF-8' ) . "\n\n" . $ex . "\n\n📞 Hotline/Zalo: " . get_option( 'dtfb_hotline', '0971 024 840' );
	}
	if ( get_option( 'dtfb_add_link', '0' ) === '1' && strpos( $m, get_permalink( $post ) ) === false ) {
		$m .= "\n👉 Xem chi tiết: " . get_permalink( $post );
	}
	return $m;
}

function dtfb_publish( $post_id, $force = false, $when = 0 ) {
	$post = get_post( $post_id );
	if ( ! $post || 'publish' !== $post->post_status || ! in_array( $post->post_type, DTFB_TYPES, true ) ) { return; }
	if ( ! $force && get_post_meta( $post_id, 'dtfb_fb_id', true ) ) { return; }
	if ( get_post_meta( $post_id, 'dtfb_skip', true ) === '1' && ! $force ) { return; }
	$when  = (int) $when;
	$extra = $when > time() + 600 ? array( 'published' => 'false', 'scheduled_publish_time' => $when ) : array( 'published' => 'true' );
	$page = get_option( 'dtfb_page_id' );
	$msg  = dtfb_message( $post );
	$img  = get_the_post_thumbnail_url( $post, 'full' );
	if ( $img ) {
		$r = dtfb_api_post( $page . '/photos', array_merge( array( 'url' => $img, 'message' => $msg ), $extra ) );
	} else {
		$r = dtfb_api_post( $page . '/feed', array_merge( get_option( 'dtfb_add_link', '0' ) === '1' ? array( 'message' => $msg, 'link' => get_permalink( $post ) ) : array( 'message' => $msg ), $extra ) );
	}
	$now = current_time( 'mysql' );
	if ( is_wp_error( $r ) ) {
		update_post_meta( $post_id, 'dtfb_status', 'Lỗi ' . $now . ': ' . $r->get_error_message() );
		update_option( 'dtfb_last_log', $now . ' – LỖI – ' . get_the_title( $post ) . ': ' . $r->get_error_message(), false );
		return $r;
	}
	$fb = $r['post_id'] ?? ( $r['id'] ?? '' );
	if ( isset( $extra['scheduled_publish_time'] ) ) {
		$t = wp_date( 'd/m/Y H:i', $when );
		update_post_meta( $post_id, 'dtfb_fb_id', $fb );
		update_post_meta( $post_id, 'dtfb_status', 'Đã hẹn lịch đăng lúc ' . $t . ' (ID ' . $fb . ')' );
		update_option( 'dtfb_last_log', $now . ' – Hẹn lịch ' . $t . ' – ' . get_the_title( $post ), false );
		return $r;
	}
	update_post_meta( $post_id, 'dtfb_fb_id', $fb );
	update_post_meta( $post_id, 'dtfb_status', 'Đã đăng ' . $now . ' (ID ' . $fb . ')' );
	update_option( 'dtfb_last_log', $now . ' – Đã đăng – ' . get_the_title( $post ) . ' (ID ' . $fb . ')', false );
	return $r;
}

/* Kiểm tra bài đã hẹn lịch / trạng thái bài trên Fanpage (chỉ quản trị viên) */
add_action( 'rest_api_init', function () {
	register_rest_route( 'dtfb/v1', '/fbcheck', array(
		'methods'             => 'GET',
		'permission_callback' => function () { return current_user_can( 'manage_options' ); },
		'callback'            => function ( $req ) {
			$page = get_option( 'dtfb_page_id' );
			$out  = array();
			$out['scheduled'] = dtfb_api_get( $page . '/scheduled_posts', array( 'fields' => 'id,message,scheduled_publish_time,is_published', 'limit' => 50 ) );
			$ids = array_filter( array_map( 'trim', explode( ',', (string) $req['ids'] ) ) );
			foreach ( $ids as $i ) {
				$out['posts'][ $i ] = dtfb_api_get( $i, array( 'fields' => 'is_published,scheduled_publish_time,created_time,permalink_url' ) );
			}
			foreach ( $out as $k => $v ) { if ( is_wp_error( $v ) ) { $out[ $k ] = $v->get_error_message(); } }
			if ( isset( $out['posts'] ) ) { foreach ( $out['posts'] as $k => $v ) { if ( is_wp_error( $v ) ) { $out['posts'][ $k ] = $v->get_error_message(); } } }
			return $out;
		},
	) );
} );

/* Huỷ bài đã hẹn lịch (chưa đăng) do plugin tạo – chỉ quản trị viên */
add_action( 'rest_api_init', function () {
	register_rest_route( 'dtfb/v1', '/fbcancel', array(
		'methods'             => 'POST',
		'permission_callback' => function () { return current_user_can( 'manage_options' ); },
		'callback'            => function ( $req ) {
			$id  = (int) $req['id'];
			$fb  = get_post_meta( $id, 'dtfb_fb_id', true );
			if ( ! $fb ) { return new WP_Error( 'dtfb', 'Không có bài Facebook.', array( 'status' => 400 ) ); }
			$full = strpos( $fb, '_' ) === false ? get_option( 'dtfb_page_id' ) . '_' . $fb : $fb;
			$chk  = dtfb_api_get( $full, array( 'fields' => 'is_published' ) );
			if ( is_wp_error( $chk ) ) { return new WP_Error( 'dtfb', $chk->get_error_message(), array( 'status' => 400 ) ); }
			if ( ! empty( $chk['is_published'] ) ) { return new WP_Error( 'dtfb', 'Bài đã đăng – không huỷ.', array( 'status' => 400 ) ); }
			$tok = get_option( 'dtfb_token' );
			$res = dtfb_parse( wp_remote_request( DTFB_API . $full . '?access_token=' . rawurlencode( $tok ), array( 'method' => 'DELETE', 'timeout' => 20 ) ) );
			if ( is_wp_error( $res ) ) { return new WP_Error( 'dtfb', $res->get_error_message(), array( 'status' => 400 ) ); }
			delete_post_meta( $id, 'dtfb_fb_id' );
			update_post_meta( $id, 'dtfb_status', 'Đã huỷ lịch cũ ' . current_time( 'mysql' ) );
			return array( 'id' => $id, 'deleted' => $full );
		},
	) );
} );

/* Đăng hoặc hẹn lịch từ xa: POST /wp-json/dtfb/v1/push {id, when(unix, tùy chọn)} */
add_action( 'rest_api_init', function () {
	register_rest_route( 'dtfb/v1', '/push', array(
		'methods'             => 'POST',
		'permission_callback' => function ( $req ) { return current_user_can( 'edit_post', (int) $req['id'] ); },
		'callback'            => function ( $req ) {
			$id = (int) $req['id'];
			$r  = dtfb_publish( $id, true, (int) $req['when'] );
			if ( is_wp_error( $r ) ) { return new WP_Error( 'dtfb', $r->get_error_message(), array( 'status' => 400 ) ); }
			return array( 'id' => $id, 'status' => get_post_meta( $id, 'dtfb_status', true ) );
		},
	) );
} );

/* Khi chuyển sang "publish": chạy ở cuối request để ảnh/meta đã lưu xong */
add_action( 'transition_post_status', function ( $new, $old, $post ) {
	if ( 'publish' !== $new || 'publish' === $old ) { return; }
	if ( get_option( 'dtfb_enabled', '1' ) !== '1' ) { return; }
	if ( ! in_array( $post->post_type, DTFB_TYPES, true ) ) { return; }
	$id = $post->ID;
	add_action( 'shutdown', function () use ( $id ) { dtfb_publish( $id ); } );
}, 10, 3 );

/* ---------- Hộp trong trang sửa bài ---------- */
add_action( 'add_meta_boxes', function () {
	foreach ( DTFB_TYPES as $t ) {
		add_meta_box( 'dtfb_box', 'Đăng Facebook', 'dtfb_box', $t, 'side' );
	}
} );
function dtfb_box( $post ) {
	wp_nonce_field( 'dtfb_box', 'dtfb_box_nonce' );
	$st = get_post_meta( $post->ID, 'dtfb_status', true );
	echo '<p><textarea name="dtfb_message" rows="8" style="width:100%" placeholder="Nội dung Facebook (để trống = tự lấy tiêu đề + mô tả ngắn, không gắn link)">' . esc_textarea( get_post_meta( $post->ID, 'dtfb_message', true ) ) . '</textarea></p>';
	echo '<p><label><input type="checkbox" name="dtfb_skip" value="1" ' . checked( get_post_meta( $post->ID, 'dtfb_skip', true ), '1', false ) . '> Không đăng bài này lên Facebook</label></p>';
	if ( 'publish' === $post->post_status ) {
		echo '<p><label><input type="checkbox" name="dtfb_repost" value="1"> Đăng lại lên Facebook khi bấm Cập nhật</label></p>';
	}
	echo '<p style="color:#555">' . esc_html( $st ? $st : 'Chưa đăng Facebook.' ) . '</p>';
}
add_action( 'save_post', function ( $post_id ) {
	if ( ! isset( $_POST['dtfb_box_nonce'] ) || ! wp_verify_nonce( sanitize_text_field( wp_unslash( $_POST['dtfb_box_nonce'] ) ), 'dtfb_box' ) ) { return; }
	if ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE ) { return; }
	if ( ! current_user_can( 'edit_post', $post_id ) ) { return; }
	update_post_meta( $post_id, 'dtfb_message', sanitize_textarea_field( wp_unslash( $_POST['dtfb_message'] ?? '' ) ) );
	update_post_meta( $post_id, 'dtfb_skip', isset( $_POST['dtfb_skip'] ) ? '1' : '0' );
	if ( ! empty( $_POST['dtfb_repost'] ) ) {
		add_action( 'shutdown', function () use ( $post_id ) { dtfb_publish( $post_id, true ); } );
	}
} );

/* Cho phép đọc/ghi qua REST (để soạn nội dung Facebook từ xa) */
add_action( 'init', function () {
	foreach ( DTFB_TYPES as $t ) {
		foreach ( array( 'dtfb_message', 'dtfb_status', 'dtfb_fb_id', 'dtfb_skip' ) as $k ) {
			register_post_meta( $t, $k, array( 'type' => 'string', 'single' => true, 'show_in_rest' => true, 'auth_callback' => function () { return current_user_can( 'edit_posts' ); } ) );
		}
	}
} );
