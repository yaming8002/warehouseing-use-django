var conditionMet = false;

async function totalUpload(file) {
    if (file) {
        // 顯示載入指示器
        $("#base_table tbody").empty();
        showSpinner();

        $('#update_text').text("移除舊資料....");
        var filename = file.name;
        var pattern = /(\d+)年(\d+)月/;  // 正規表達式模式
        console.log(filename);
        var match = filename.match(pattern);

        if (match) {
            var yearChinese = parseInt(match[1]);
            var month = parseInt(match[2]);

            // 轉換年份，中華民國年轉換為西元年
            var yearAD = 1911 + yearChinese;
            await $.ajax({
                url: '/transport_log/move_old_data/',
                data: { "yearmonth": yearAD + '-' + month },
                method: 'GET'
            });
        }

        $('#update_text').text("EXCEL 分析中....");
        await handleFileProcessing(file); // Await to ensure the whole process completes
    } else {
        alert("請先選擇一個檔。");
    }
}

function waitForConditionToBeTrue(conditionVariable) {
    return new Promise(resolve => {
        const intervalId = setInterval(() => {
            if (conditionVariable) {
                clearInterval(intervalId);
                resolve();
            }
        }, 100); // 每100毫秒檢查一次
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // 判斷這個cookie的名稱是否等於所查找的名稱
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function checkColumns(columns, input) {
    const cleanedColumns = columns.filter(item => item !== null && item.trim() !== "").map(item => item.replace(/\s+/g, ''));
    return columns.length === cleanedColumns.length && columns.every((col, index) => col === cleanedColumns[index]);
}

async function handleFileProcessing(file) {
    const csrftoken = getCookie('csrftoken');
    const reader = new FileReader();
    let count_date = null;

    reader.onload = async function (e) {
        const data = new Uint8Array(e.target.result);
        const workbook = XLSX.read(data, { type: 'array' });
        const total_rows = XLSX.utils.sheet_to_json(workbook.Sheets["總表"], { header: 1 });
        const rent_rows = XLSX.utils.sheet_to_json(workbook.Sheets["租賃"], { header: 1 });
        const index_rows = XLSX.utils.sheet_to_json(workbook.Sheets["Index"], { header: 1 });

        // Process carbcData
        const carbcData = index_rows.slice(1, 2000).map(row => ({
            car_number: row[19],
            car_firm: row[20],
            remark: row[21],
            value: row[22]
        }));

        // Ensure this is awaited for proper flow
        await uploadData('/carinfo/uploadexcelByTotal/', carbcData, csrftoken);

        // Process siteinfo in batches
        const siteinfo = index_rows.slice(2, 2000).map(row => ({
            code: row[9],
            owner: row[10],
            name: row[11]
        }));
        await uploadData('/constn/uploadexcelByTotal/', siteinfo, csrftoken);

        // Process other rows if any
        if (total_rows.length > 0 || rent_rows.length > 1) {
            count_date = total_rows.slice(4)[5][1];
            console.log('count_date is ' + count_date);
            // 驗證列名
            if (checkColumns(columns3, total_rows[2]) && checkColumns(columns4, total_rows[3])) {
                // 如果驗證通過，則處理並分批上傳資料
                await processAndUploadData(count_date, total_rows.slice(4), false, csrftoken);
            } else {
                alert("總表檔案格式不正確");
            }

            if (checkColumns(columns3, rent_rows[2]) && checkColumns(columns4, rent_rows[3])) {
                await processAndUploadData(count_date, rent_rows.slice(4), true, csrftoken);
            } else {
                alert("租賃檔案格式不正確");
            }
        }
    };

    reader.readAsArrayBuffer(file);
}

async function uploadData(url, data, csrftoken, is_item = false) {
    try {
        await $.ajax({
            url: url,
            type: 'POST',
            contentType: 'application/json',
            headers: { 'X-CSRFToken': csrftoken },
            data: JSON.stringify(data),
            success: function (data) {
                if (is_item) {
                    data.error_list.forEach(item => {
                        const tr = $('<tr></tr>').append(`<td>${item.e}</td>`);
                        item.item.slice(1).forEach((col, index) => {
                            if (index + 1 === 1 || index + 1 === 27) {
                                let formattedDate = formatDate(col); // Format to "Y-m-d"
                                tr.append(`<td>${formattedDate}</td>`); // Append formatted date
                            } else {
                                tr.append(`<td>${col || ''}</td>`);
                            }

                        });
                        $("#base_table tbody").append(tr);
                    });
                }
            }
        });

    } catch (error) {
        console.error('Error uploading data:', error);

    }
}
/*
async function uploadInBatches(url, data, csrftoken) {
    const batchSize = 100;
    for (let i = 0; i < data.length; i += batchSize) {
        const batch = data.slice(i, i + batchSize);
        await uploadData(url, batch, csrftoken,3000);
        console.log(`Batch ${i + 1} uploaded successfully.`);
    }
}
*/
async function processAndUploadData(count_date, rows, is_rent, csrftoken) {
    const batchSize = 100;
    let batchData = [];
    let is_all = $('#is_all').is(':checked');
    const end_date = new Date();  // Assuming end_date is defined elsewhere

    for (let i = 0; i < rows.length; i++) {
        if (end_date < rows[i][1] || is_all) {
            batchData.push(rows[i]);
        }

        if (batchData.length === batchSize || rows[i].length < 2 || !rows[i][6]) {
            $('#update_text').text(`上傳...${i}/${rows.length}`);
            await uploadData(url, { jsonData: batchData, is_rent: is_rent }, csrftoken, true);
            console.log(`Batch ${i + 1} uploaded successfully.`);
            batchData = [];
        }

        if (rows[i].length < 2 || !rows[i][6]) {
            break; // Exit loop if incomplete data
        }
    }

    if (is_rent) {
        try {
            await $.ajax({
                url: "/update_end_date/",
                data: { "count_date": formatDate(count_date) },
                method: 'GET'
            });
            alert("上傳完成");
            hideSpinner();
        } catch (error) {
            console.error("更新結束日期過程中出現錯誤：", error);
        }
    }
}

function excelDateToJSDate(excelDate) {
    const date = new Date(1899, 11, 30);
    date.setDate(date.getDate() + excelDate);
    return date;
}

function formatDate(date) {
    let d = excelDateToJSDate(date);
    let month = '' + (d.getMonth() + 1);
    let day = '' + d.getDate();
    let year = d.getFullYear();

    if (month.length < 2) month = '0' + month;
    if (day.length < 2) day = '0' + day;
    return [year, month, day].join('-');
}

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
