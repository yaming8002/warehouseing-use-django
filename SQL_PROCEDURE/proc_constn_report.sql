DELIMITER $$
DROP PROCEDURE IF EXISTS proc_constn_report_summary;

CREATE PROCEDURE proc_constn_report_summary (
    IN begin_date DATETIME,
    IN end_date DATETIME
)
BEGIN
    -- 創建臨時表 temp_components
    DROP TEMPORARY TABLE IF EXISTS temp_components;
    CREATE TEMPORARY TABLE temp_components AS
        SELECT id, mat_code, name FROM w_stock_materials WHERE component > 0;

    -- 創建臨時表 temp_tools
    DROP TEMPORARY TABLE IF EXISTS temp_tools;
    CREATE TEMPORARY TABLE temp_tools AS
        SELECT id, mat_code, name FROM w_stock_materials WHERE tool_report = TRUE;

    -- 創建臨時表 temp_brace
    DROP TEMPORARY TABLE IF EXISTS temp_brace;
    CREATE TEMPORARY TABLE temp_brace (
        id BIGINT,
        mat_code VARCHAR(10),
        name VARCHAR(20)
    );

    -- 插入 support_list 的數據
    INSERT INTO temp_brace (id, mat_code, `name`) VALUES
        (358,'300', 'H300'),
        (295,'350', 'H350'),
        (424,'400', 'H400'),
        (170,'408', 'H408');

    -- 創建臨時表 temp_steel_level
    DROP TEMPORARY TABLE IF EXISTS temp_steel_level;
    CREATE TEMPORARY TABLE temp_steel_level AS
    SELECT
        d.translog_id,
        CASE
            WHEN m.mat_code IN (SELECT mat_code FROM temp_brace) THEN (SELECT id FROM temp_brace WHERE mat_code = m.mat_code)
            ELSE m.id
        END AS material_id,
        SUM(d.quantity) AS quantity,
        SUM(d.all_unit) AS unit,
        d.remark,
        COALESCE(d.level, 0) AS `level`
    FROM
        w_trans_translogdetail AS d
    INNER JOIN
        w_trans_translog AS tg ON d.translog_id = tg.id
    INNER JOIN
        w_stock_materials AS m ON d.material_id = m.id
    WHERE
        tg.build_date BETWEEN begin_date AND end_date
        AND d.remark NOT LIKE '%#%'
        AND tg.constn_site_id <> 1
    GROUP BY
        d.translog_id,
         CASE
            WHEN m.mat_code IN (SELECT mat_code FROM temp_brace) THEN (SELECT id FROM temp_brace WHERE mat_code = m.mat_code)
            ELSE m.id
        END,
        d.remark,
        COALESCE(d.level, 0) ;

    -- 插入到 w_constn_levelbrace 表
    INSERT INTO `warehousingdb`.`w_constn_levelbrace`
        (`translog_id`, `html_name`, `level`, `material_id`, `quantity`, `unit`, `remark`, `is_mid`)
    SELECT
        t.translog_id,
        s.name,
        t.level,
        s.id,
        SUM(t.quantity) AS quantity,
        SUM(t.unit) AS unit,
        t.remark,
        FALSE
    FROM
        temp_steel_level AS t
    INNER JOIN
        temp_brace AS s ON t.material_id = s.id;
    GROUP BY
        t.translog_id,
        s.name,
        t.level,
        s.id,
        t.remark ;


    -- 插入到 w_constn_levelcomponent 表
    INSERT INTO `warehousingdb`.`w_constn_levelcomponent`
        (`translog_id`, `html_name`, `level`, `material_id`, `quantity`, `unit`, `remark`, `is_mid`)
    SELECT
        t.translog_id,
        s.name,
        t.level,
        s.id,
        t.quantity,
        t.unit,
        t.remark,
        FALSE
    FROM
        temp_steel_level AS t
    INNER JOIN
        temp_components AS s ON t.material_id = s.id;
    GROUP BY
        t.translog_id,
        s.name,
        t.level,
        s.id,
        t.remark ;

    -- 插入到 w_constn_leveltool 表
    INSERT INTO `warehousingdb`.`w_constn_leveltool`
        (`translog_id`, `html_name`, `level`, `material_id`, `quantity`, `unit`, `remark`, `is_mid`)
    SELECT
        t.translog_id,
        s.name,
        t.level,
        s.id,
        t.quantity,
        t.unit,
        t.remark,
        FALSE
    FROM
        temp_steel_level AS t
    INNER JOIN
        temp_tools AS s ON t.material_id = s.id;
    GROUP BY
        t.translog_id,
        s.name,
        t.level,
        s.id,
        t.remark ;

    -- 刪除臨時表
    DROP TEMPORARY TABLE IF EXISTS temp_components;
    DROP TEMPORARY TABLE IF EXISTS temp_tools;
    DROP TEMPORARY TABLE IF EXISTS temp_brace;
    DROP TEMPORARY TABLE IF EXISTS temp_steel_level;

END $$

DELIMITER ;
