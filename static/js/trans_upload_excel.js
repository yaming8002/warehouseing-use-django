var conditionMet = false;


async function totalUpload(file) {
    if (file) {
        // 顯示載入指示器
        $("#base_table tbody").empty();
        showSpinner();
        $('#update_text').text("EXCEL 分析中....");
        handleFileProcessing(file);
    } else {
        // 如果沒有選擇檔，則提示用戶
        alert("請先選擇一個檔。");
    }
}

// 模擬一個設置conditionMet為true的異步操作
function simulateAsyncOperation() {
    setTimeout(() => {
        conditionMet = true;
    }, 5000); // 模擬一個耗時5秒的異步操作
}

async function performActions() {
    console.log("正在等待條件成立...");
    await waitForConditionToBeTrue(conditionMet);
    console.log("條件已成立，繼續執行剩餘代碼。");

    // 繼續執行你的代碼
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
    let count_date = null ;
    reader.onload = async function (e) {
        const data = new Uint8Array(e.target.result);
        const workbook = XLSX.read(data, { type: 'array' });
        // 轉換工作表資料為JSON
        const total_rows = XLSX.utils.sheet_to_json(workbook.Sheets["總表"], {
            header: 1
        });
        const rent_rows = XLSX.utils.sheet_to_json(workbook.Sheets["租賃"], {
            header: 1
        });
        const index_rows = XLSX.utils.sheet_to_json(workbook.Sheets["Index"], {
            header: 1
        });
        
        var carbcData = index_rows.slice(1, 2000).map(row => ({
            car_number: row[19],  // U 列
            car_firm: row[20],   // V 列
            remark: row[21],  // W 列
            value: row[22]   // X 列
        }));

        await $.ajax({
            url: '/carinfo/uploadexcelByTotal/',  // 替換為你的後台地址
            type: 'POST',
            contentType: 'application/json',
            headers: { 'X-CSRFToken': csrftoken },
            data: JSON.stringify(carbcData),
            success: function (response) {
                console.log('Data uploaded successfully:', response);
            },
            error: function (xhr, status, error) {
                console.log('Error uploading data:', error);
            }
        });

        var siteinfo = index_rows.slice(2, 2000).map(row => ({
            code: row[9],  // K 列
            owner: row[10],  // L 列
            name: row[11]   // M 列
        }));

        let i = 0
        for (; i < siteinfo.length; i += 100) {
            var bcData = siteinfo.slice(i, i + 200);
            $.ajax({
                url: '/constn/uploadexcelByTotal/',
                type: 'POST',
                contentType: 'application/json',
                headers: { 'X-CSRFToken': csrftoken },
                data: JSON.stringify(bcData)
            });
            console.log(`Batch ${i + 1} uploaded successfully:`);
        }

        var bcData = siteinfo.slice(i);
        await $.ajax({
            url: '/constn/uploadexcelByTotal/',
            type: 'POST',
            contentType: 'application/json',
            headers: { 'X-CSRFToken': csrftoken },
            data: JSON.stringify(bcData),
            success: function (data) {
                conditionMet = false;
            }
        });
        if (total_rows.length > 0 || rent_rows.length > 1) {
            count_date = total_rows.slice(4)[5][1]
            console.log('count_date is ' + count_date) ;
            // 驗證列名
            if (checkColumns(columns3, total_rows[2]) & checkColumns(columns4, total_rows[3])) {
                // 如果驗證通過，則處理並分批上傳資料
                await processAndUploadData(count_date,total_rows.slice(4), false,csrftoken); // 移除列名行
            } else {
                alert("總表檔案格式不正確");
            }

            if (checkColumns(columns3, rent_rows[2]) & checkColumns(columns4, rent_rows[3])) {
                await processAndUploadData(count_date,rent_rows.slice(4), true,csrftoken); // 移除列名行
            } else {
                alert("租賃檔案格式不正確");
            }
        }

    };
    await reader.readAsArrayBuffer(file);
}


async function processAndUploadData( count_date , rows, is_rent,csrftoken) {
    const batchSize = 50;
    let batchData = [];

    for (let i = 0; i < rows.length; i++) {

        if (end_date < rows[i][1]) {
            batchData.push(rows[i]);
        }

        // Upload when batch is full or at the end of array
        if (batchData.length === batchSize || rows[i].length < 2 || !rows[i][6]) {
            $('#update_text').text("上傳..." + i + "/" + rows.length);
            try {
                await $.ajax({
                    url: url,
                    type: 'POST',
                    contentType: 'application/json; charset=utf-8',
                    headers: { 'X-CSRFToken': csrftoken },
                    data: JSON.stringify({ jsonData: batchData, is_rent: is_rent }),
                    dataType: 'json',
                    success: function (data) {
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
                });

            } catch (error) {
                console.error("上傳資料過程中出現錯誤：", error);
            }
            batchData = []; // Clear the batch data after upload
            if (rows[i].length < 2 || !rows[i][6]) {
                break; // Skip the rest if data is incomplete
            }
        }
    }

    // Update the end date if applicable
    if (is_rent) {
        console.log('count_date is ' + count_date) ;
        try {
            await $.ajax({
                url: "/update_end_date/",
                data:{"count_date":formatDate(count_date)},
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
    const date = new Date(1899, 11, 30); // 月份从 0 开始，11 代表 12 月
    date.setDate(date.getDate() + excelDate ); 
    return date;
  }

function formatDate(date) {
    let d = excelDateToJSDate(date)
    let month = '' + (d.getMonth()+ 1), // getUTCMonth returns 0-11
        day = '' + d.getDate(),
        year = d.getFullYear();

    if (month.length < 2) month = '0' + month; // padding single-digit months
    if (day.length < 2) day = '0' + day; // padding single-digit days
    return [year, month, day].join('-'); // joining components with '-'
}