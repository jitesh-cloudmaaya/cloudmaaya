SET SESSION group_concat_max_len=5000;

SELECT
    wu.id,
    wu.first_name,
    wu.last_name,
    sa.address_1,
    sa.address_2,
    sa.city,
    sa.state,
    sa.country,
    quiz.birthday,
    quiz.occupation,
    quiz.wear_to_work,
    quiz.spend_free_time,
    quiz.where_live,
    quiz.time_of_day_text,
    quiz.social_media,
    quiz.instagram,
    quiz.pinterest,
    quiz.linkedin,
    quiz.photo,
    styling_sessions.styling_count,
    styling_sessions.last_styling_date,
    order_summary.order_count,
    last_ord_amt.amt   AS last_order_amt,
    order_summary.last_order_date,
    order_summary.avg_items,
    order_summary.avg_amt,
    social_actions.heart_count,
    social_actions.comment_count,
    social_actions.star_count,
    wu.user_registered AS signup_date,
    ac.utm_source,
    ac.utm_campaign,
    ac.utm_term,
    ac.utm_medium,
    quiz.hear_about_allume,
    quiz.height,
    quiz.weight,
    quiz.bra_size,
    quiz.body_part_attention,
    quiz.body_part_conceal,
    quiz.fit_challenges,
    quiz.hair_complex_color,
    quiz.first_session_focus,
    quiz.looks_goal,
    quiz.pieces_focus,
    quiz.outfits_preference,
    quiz.other_goals,
    quiz.stores,
    quiz.brands,
    quiz.spending_tops,
    quiz.spending_bottoms,
    quiz.spending_dresses,
    quiz.spending_jackets,
    quiz.spending_shoes,
    quiz.style_celebs,
    quiz.style_looks,
    quiz.style_jeans,
    quiz.style_tops,
    quiz.style_dress,
    quiz.style_jacket,
    quiz.style_shoe,
    quiz.colors_preference,
    quiz.style_avoid,
    quiz.size_pants,
    quiz.size_jeans,
    quiz.size_tops,
    quiz.size_shoe,
    quiz.ears_pierced,
    quiz.jewelry_style,
    quiz.jewelry_type
  FROM
    wp_users wu
    LEFT JOIN
    allume_wp_user_shipping_addresses sa
      ON wu.ID = sa.wp_user_id
    LEFT JOIN
    (SELECT
       COUNT(*)                                     styling_count,
       COALESCE(MAX(start_date), MAX(date_created)) last_styling_date,
       wp_initiator_id
     FROM
       allume_styling_sessions
     GROUP BY
       wp_initiator_id
    ) styling_sessions
      ON wu.ID = styling_sessions.wp_initiator_id
    LEFT JOIN
    allume_clients ac
      ON wu.ID = ac.wp_client_id
    LEFT JOIN
    (SELECT
       user_email,
       GROUP_CONCAT(if(quiz_question_answer_id = 28, label, NULL) SEPARATOR ', ') AS birthday,
       GROUP_CONCAT(if(quiz_question_answer_id = 29, label, NULL) SEPARATOR ', ') AS occupation,
       GROUP_CONCAT(if(quiz_question_answer_id = 30, label, NULL) SEPARATOR ', ') AS wear_to_work,
       GROUP_CONCAT(if(quiz_question_answer_id = 31, label, NULL) SEPARATOR ', ') AS spend_free_time,
       GROUP_CONCAT(if(quiz_question_answer_id = 27, label, NULL) SEPARATOR ', ') AS where_live,
       GROUP_CONCAT(if(quiz_question_answer_id = 48, label, NULL) SEPARATOR ', ') AS time_of_day_text,
       GROUP_CONCAT(if(quiz_question_answer_id = 32, label, NULL) SEPARATOR ', ') AS social_media,
       GROUP_CONCAT(if(quiz_question_answer_id = 33, label, NULL) SEPARATOR ', ') AS instagram,
       GROUP_CONCAT(if(quiz_question_answer_id = 34, label, NULL) SEPARATOR ', ') AS pinterest,
       GROUP_CONCAT(if(quiz_question_answer_id = 35, label, NULL) SEPARATOR ', ') AS linkedin,
       GROUP_CONCAT(if(quiz_question_answer_id = 36, label, NULL) SEPARATOR ', ') AS photo,
       GROUP_CONCAT(if(quiz_question_answer_id = 47, label, NULL) SEPARATOR ', ') AS hear_about_allume,
       GROUP_CONCAT(if(quiz_question_answer_id = 14, label, NULL) SEPARATOR ', ') AS height,
       GROUP_CONCAT(if(quiz_question_answer_id = 15, label, NULL) SEPARATOR ', ') AS weight,
       GROUP_CONCAT(if(quiz_question_answer_id = 16, label, NULL) SEPARATOR ', ') AS bra_size,
       GROUP_CONCAT(if(quiz_question_answer_id = 20, label, NULL) SEPARATOR ', ') AS body_part_attention,
       GROUP_CONCAT(if(quiz_question_answer_id = 21, label, NULL) SEPARATOR ', ') AS body_part_conceal,
       GROUP_CONCAT(if(quiz_question_answer_id = 22, label, NULL) SEPARATOR ', ') AS fit_challenges,
       GROUP_CONCAT(if(quiz_question_answer_id = 13, label, NULL) SEPARATOR ', ') AS hair_complex_color,
       GROUP_CONCAT(if(quiz_question_answer_id = 42, label, NULL) SEPARATOR ', ') AS first_session_focus,
       GROUP_CONCAT(if(quiz_question_answer_id = 43, label, NULL) SEPARATOR ', ') AS looks_goal,
       GROUP_CONCAT(if(quiz_question_answer_id = 44, label, NULL) SEPARATOR ', ') AS pieces_focus,
       GROUP_CONCAT(if(quiz_question_answer_id = 45, label, NULL) SEPARATOR ', ') AS outfits_preference,
       GROUP_CONCAT(if(quiz_question_answer_id = 46, label, NULL) SEPARATOR ', ') AS other_goals,
       GROUP_CONCAT(if(quiz_question_answer_id = 3, label, NULL) SEPARATOR ', ')  AS stores,
       GROUP_CONCAT(if(quiz_question_answer_id = 5, label, NULL) SEPARATOR ', ')  AS brands,
       GROUP_CONCAT(if(quiz_question_answer_id = 37, label, NULL) SEPARATOR ', ') AS spending_tops,
       GROUP_CONCAT(if(quiz_question_answer_id = 38, label, NULL) SEPARATOR ', ') AS spending_bottoms,
       GROUP_CONCAT(if(quiz_question_answer_id = 39, label, NULL) SEPARATOR ', ') AS spending_dresses,
       GROUP_CONCAT(if(quiz_question_answer_id = 40, label, NULL) SEPARATOR ', ') AS spending_jackets,
       GROUP_CONCAT(if(quiz_question_answer_id = 41, label, NULL) SEPARATOR ', ') AS spending_shoes,
       GROUP_CONCAT(if(quiz_question_answer_id = 1, label, NULL) SEPARATOR ', ')  AS style_celebs,
       GROUP_CONCAT(if(quiz_question_answer_id = 2, label, NULL) SEPARATOR ', ')  AS style_looks,
       GROUP_CONCAT(if(quiz_question_answer_id = 6, label, NULL) SEPARATOR ', ')  AS style_jeans,
       GROUP_CONCAT(if(quiz_question_answer_id = 7, label, NULL) SEPARATOR ', ')  AS style_tops,
       GROUP_CONCAT(if(quiz_question_answer_id = 8, label, NULL) SEPARATOR ', ')  AS style_dress,
       GROUP_CONCAT(if(quiz_question_answer_id = 9, label, NULL) SEPARATOR ', ')  AS style_jacket,
       GROUP_CONCAT(if(quiz_question_answer_id = 10, label, NULL) SEPARATOR ', ') AS style_shoe,
       GROUP_CONCAT(if(quiz_question_answer_id = 11, label, NULL) SEPARATOR ', ') AS colors_preference,
       GROUP_CONCAT(if(quiz_question_answer_id = 12, label, NULL) SEPARATOR ', ') AS style_avoid,
       GROUP_CONCAT(if(quiz_question_answer_id = 23, label, NULL) SEPARATOR ', ') AS size_pants,
       GROUP_CONCAT(if(quiz_question_answer_id = 24, label, NULL) SEPARATOR ', ') AS size_jeans,
       GROUP_CONCAT(if(quiz_question_answer_id = 25, label, NULL) SEPARATOR ', ') AS size_tops,
       GROUP_CONCAT(if(quiz_question_answer_id = 26, label, NULL) SEPARATOR ', ') AS size_shoe,
       GROUP_CONCAT(if(quiz_question_answer_id = 17, label, NULL) SEPARATOR ', ') AS ears_pierced,
       GROUP_CONCAT(if(quiz_question_answer_id = 18, label, NULL) SEPARATOR ', ') AS jewelry_style,
       GROUP_CONCAT(if(quiz_question_answer_id = 19, label, NULL) SEPARATOR ', ') AS jewelry_type
     FROM
       (SELECT
          qua.user_email,
          qua.quiz_question_answer_id,
          qai.label
        FROM
          allume_quiz_answer_items qai,
          allume_quiz_user_answers qua
        WHERE
          FIND_IN_SET(qai.ID, qua.quiz_answer_item_ids) AND
          qai.type <> 'free_form' AND
          qai.label <> ''
          $QUIZ_ANSWER_USER_FILTER_AND_CLAUSE
        UNION
        SELECT
          qua2.user_email,
          qua2.quiz_question_answer_id,
          qua2.quiz_free_form_answer
        FROM
          allume_quiz_user_answers qua2
        WHERE
          qua2.quiz_free_form_answer IS NOT NULL
          $QUIZ_ANSWER2_USER_FILTER_AND_CLAUSE) user_answers
     GROUP BY user_email) quiz
      ON wu.user_email = quiz.user_email

    -- Q2 End
    LEFT JOIN
    (SELECT
       COUNT(*)        AS order_count,
       MAX(order_date) AS last_order_date,
       AVG(items)      AS avg_items,
       AVG(amt)        AS avg_amt,
       wp_user_id
     FROM
       order_list
     GROUP BY wp_user_id) order_summary
      ON wu.ID = order_summary.wp_user_id
    LEFT JOIN
    (SELECT
       ol.wp_user_id,
       sum(ol.amt) as amt # Andrew's change
     FROM
       order_list ol
       INNER JOIN
       (SELECT
          wp_user_id,
          MAX(order_date) AS last_order_date
        FROM order_list
        GROUP BY wp_user_id) AS lod ON
                                      lod.last_order_date = ol.order_date
                                      AND lod.wp_user_id = ol.wp_user_id
    GROUP BY ol.wp_user_id, ol.order_date) last_ord_amt   # Andrew's change
      ON wu.ID = last_ord_amt.wp_user_id
    LEFT JOIN
    (SELECT
       user_id,
       count(CASE WHEN action = 'hearted'
         THEN 1 END) heart_count,
       count(CASE WHEN action = 'commented'
         THEN 1 END) comment_count,
       count(CASE WHEN action = 'starred'
         THEN 1 END) star_count
     FROM
       allume_social_actions
     GROUP BY
       user_id) social_actions
      ON wu.ID = social_actions.user_id

$USER_FILTER
