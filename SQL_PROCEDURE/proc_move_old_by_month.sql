DELIMITER $$

DROP PROCEDURE IF EXISTS proc_move_old_by_month;

CREATE PROCEDURE proc_move_old_by_month(
    IN firstfay DATE,
    IN lastday DATE
)
BEGIN
    DECLARE yyyy INT;
    DECLARE mm INT;

    -- 從 firstfay 中取得 year 和 month
    SET yyyy = YEAR(firstfay);
    SET mm = MONTH(firstfay);

    -- 執行庫存退回動作
    CALL proc_stock_summary(firstfay, lastday, 0);

    DROP TEMPORARY TABLE IF EXISTS temp_translog_ids;
    CREATE TEMPORARY TABLE temp_translog_ids AS
    SELECT id FROM w_trans_translog WHERE build_date BETWEEN firstfay AND lastday;

    DELETE w_constn_steelpile
    FROM w_constn_steelpile
    INNER JOIN temp_translog_ids ON w_constn_steelpile.translog_id = temp_translog_ids.id;

    -- 刪除 w_constn_levelbrace 資料
    DELETE  w_constn_levelbrace
    FROM w_constn_levelbrace
    INNER JOIN temp_translog_ids ON w_constn_levelbrace.translog_id = temp_translog_ids.id;

    -- 刪除 w_constn_levelcomponent 資料
    DELETE  w_constn_levelcomponent
    FROM w_constn_levelcomponent
    INNER JOIN temp_translog_ids ON w_constn_levelcomponent.translog_id = temp_translog_ids.id;

    -- 刪除 w_constn_leveltool 資料
    DELETE  w_constn_leveltool
    FROM w_constn_leveltool
    INNER JOIN temp_translog_ids ON w_constn_leveltool.translog_id = temp_translog_ids.id;

    -- 刪除 TransLogDetail 資料
    DELETE  w_trans_translogdetail
    FROM w_trans_translogdetail
    INNER JOIN temp_translog_ids ON w_trans_translogdetail.translog_id = temp_translog_ids.id;

    -- 刪除 TransLog 資料
    DELETE  w_trans_translog
    FROM w_trans_translog
    INNER JOIN temp_translog_ids ON w_trans_translog.id = temp_translog_ids.id;

    -- 刪除臨時表
    DROP TEMPORARY TABLE IF EXISTS temp_translog_ids;

    -- 刪除未完成的 SteelReport
    DELETE FROM w_whreport_railreport
    WHERE Year = yyyy AND Month = mm AND is_done = 0;

    -- 刪除未完成的 SteelReport
    DELETE FROM w_whreport_steelreport
    WHERE Year = yyyy AND Month = mm AND is_done = 0;

    DELETE FROM w_whreport_boardreport
    WHERE Year = yyyy AND Month = mm AND close = 0;

    -- 刪除 DoneSteelReport 資料
    DELETE FROM w_whreport_donesteelreport
    WHERE Year = yyyy AND Month = mm AND done_type = 2;


END $$

DELIMITER ;
