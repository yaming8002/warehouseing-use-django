DELIMITER //

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

    -- 執行儲存過程（例如：stock_sql_command）
    CALL proc_stock_summary(firstfay, lastday, 0);

    -- 刪除 TransLogDetail 資料
    DELETE FROM w_trans_translogdetail
    WHERE translog_id IN (
        SELECT id FROM w_trans_translog
        WHERE build_date BETWEEN firstfay AND lastday
    );

    -- 刪除 SteelPile 資料
    DELETE FROM w_constn_steelpile
    WHERE translog_id IN (
        SELECT id FROM w_trans_translog
        WHERE build_date BETWEEN firstfay AND lastday
    );

    -- 刪除 w_constn_levelbrace 資料
    DELETE FROM w_constn_levelbrace
    WHERE translog_id IN (
        SELECT id FROM w_trans_translog
        WHERE build_date BETWEEN firstfay AND lastday
    );

    -- 刪除 w_constn_levelcomponent 資料
    DELETE FROM w_constn_levelcomponent
    WHERE translog_id IN (
        SELECT id FROM w_trans_translog
        WHERE build_date BETWEEN firstfay AND lastday
    );

    -- 刪除 w_constn_leveltool 資料
    DELETE FROM w_constn_leveltool
    WHERE translog_id IN (
        SELECT id FROM w_trans_translog
        WHERE build_date BETWEEN firstfay AND lastday
    );

    -- 刪除 TransLog 資料
    DELETE FROM w_trans_translog
    WHERE build_date BETWEEN firstfay AND lastday;

    -- 刪除未完成的 SteelReport
    DELETE FROM w_whreport_railreport
    WHERE Year = yyyy AND Month = mm AND is_done = 0;

    -- 刪除未完成的 SteelReport
    DELETE FROM w_whreport_steelreport
    WHERE Year = yyyy AND Month = mm AND is_done = 0;

    DELETE FROM w_whreport_boardreport
    WHERE Year = yyyy AND Month = mm AND is_mid = 0;

    -- 刪除 DoneSteelReport 資料
    DELETE FROM w_whreport_donesteelreport
    WHERE Year = yyyy AND Month = mm AND done_type = 2;
END //

DELIMITER ;
