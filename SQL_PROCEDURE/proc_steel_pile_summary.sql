DELIMITER //

CREATE OR REPLACE PROCEDURE proc_steel_pile_summary(
    IN begin_date DATETIME,
    IN end_date DATETIME,
)
BEGIN
    -- Drop and create temporary table
    DROP TEMPORARY TABLE IF EXISTS temp_steel_pile;
    CREATE TEMPORARY TABLE temp_steel_pile AS
    SELECT
        d.translog_id,
        d.material_id,
        d.quantity,
        d.all_unit,
        d.remark
    FROM
        trans_translogdetail AS d
    INNER JOIN
        trans_translog AS tg ON d.translog_id = tg.id
    WHERE
        tg.build_date BETWEEN begin_date AND end_date
        AND d.remark NOT LIKE '%#%'
        AND tg.constn_site_id <> 1;

    -- 插入到 stock_steelpile 中
    INSERT INTO `warehousingdb`.`stock_steelpile`
    (`translog_id`, `is_mid`, `is_ng`, `material_id`, `quantity`, `unit`, `remark`)
    SELECT
        t.translog_id,
        CASE
            WHEN t.remark LIKE '%構台樑%' THEN TRUE
            ELSE FALSE
        END AS `is_mid`,
        FALSE AS `is_ng`,
        CASE
            WHEN m.mat_code = '3050' THEN 244
            WHEN m.mat_code = '301' THEN 352
            WHEN m.mat_code = '351' THEN 400
            WHEN m.mat_code = '401' THEN 367
        END AS material_id,
        SUM(t.quantity) AS `quantity`,
        SUM(t.all_unit) AS `unit`,
        t.remark
    FROM
        temp_steel_pile AS t
    JOIN
        stock_materials AS m ON t.material_id = m.id
    WHERE
        m.mat_code IN ('3050', '301', '351', '401')
    GROUP BY
        t.translog_id,m.mat_code, t.remark;

    INSERT INTO `warehousingdb`.`stock_steelpile`
    (`translog_id`, `is_mid`, `is_ng`, `material_id`, `quantity`, `unit`, `remark`)
    SELECT
        t.translog_id,
        FALSE AS `is_mid`,
        TRUE AS `is_ng`,
        CASE
            WHEN m.specification_id = 25 THEN 244
            WHEN m.specification_id = 26 THEN 352
            WHEN m.specification_id = 27 THEN 400
            WHEN m.specification_id = 28 THEN 367
        END AS material_id,
        SUM(t.quantity) AS `quantity`,
        SUM(t.all_unit) AS `unit`,
        t.remark
    FROM
        temp_steel_pile AS t
    JOIN
        stock_materials AS m ON t.material_id = m.id
    WHERE
        m.mat_code = '999'
        AND m.specification_id IN (25, 26, 27, 28)
    GROUP BY
        t.translog_id,m.specification_id, t.remark;

    DROP TEMPORARY TABLE IF EXISTS temp_steel_pile;
END //

DELIMITER ;
