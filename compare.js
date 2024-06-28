function readCSV(file, callback) {
    const reader = new FileReader();
    reader.onload = () => {
        const text = reader.result;
        callback(text);
    };
    reader.readAsText(file);
}

function parseCSV(text) {
    const rows = text.split('\n').map(row => row.split(','));
    return rows;
}

function updateColumnSelects(headers1, headers2) {
    const column1Select = document.getElementById('column1');
    const column2Select = document.getElementById('column2');
    
    column1Select.innerHTML = '';
    column2Select.innerHTML = '';

    headers1.forEach(header => {
        const option = document.createElement('option');
        option.value = header;
        option.textContent = header;
        column1Select.appendChild(option);
    });

    headers2.forEach(header => {
        const option = document.createElement('option');
        option.value = header;
        option.textContent = header;
        column2Select.appendChild(option);
    });
}

function loadAndPrepareColumns() {
    const file1 = document.getElementById('file1').files[0];
    const file2 = document.getElementById('file2').files[0];

    if (!file1 || !file2) {
        alert('両方のファイルを選択してください。');
        return;
    }

    readCSV(file1, text1 => {
        const data1 = parseCSV(text1);
        const headers1 = data1[0];

        readCSV(file2, text2 => {
            const data2 = parseCSV(text2);
            const headers2 = data2[0];

            updateColumnSelects(headers1, headers2);
        });
    });
}

document.getElementById('file1').addEventListener('change', loadAndPrepareColumns);
document.getElementById('file2').addEventListener('change', loadAndPrepareColumns);

function compareCSV() {
    const file1 = document.getElementById('file1').files[0];
    const file2 = document.getElementById('file2').files[0];
    const column1 = document.getElementById('column1').value;
    const column2 = document.getElementById('column2').value;

    if (!file1 || !file2) {
        alert('両方のファイルを選択してください。');
        return;
    }

    if (!column1 || !column2) {
        alert('検索対象のカラム名を選択してください。');
        return;
    }

    readCSV(file1, text1 => {
        const data1 = parseCSV(text1);
        readCSV(file2, text2 => {
            const data2 = parseCSV(text2);
            const headers1 = data1[0];
            const headers2 = data2[0];

            const columnIndex1 = headers1.indexOf(column1);
            const columnIndex2 = headers2.indexOf(column2);

            if (columnIndex1 === -1 || columnIndex2 === -1) {
                alert('カラムインデックスの取得に失敗しました。');
                return;
            }

            const data1Set = new Set(data1.slice(1).map(row => row[columnIndex1]));
            const data2Set = new Set(data2.slice(1).map(row => row[columnIndex2]));

            const uniqueData1 = data1.slice(1).filter(row => !data2Set.has(row[columnIndex1]));
            const uniqueData2 = data2.slice(1).filter(row => !data1Set.has(row[columnIndex2]));
            const uniqueData = uniqueData1.concat(uniqueData2);
            uniqueData.unshift(headers1); // add headers to the result

            downloadCSV(uniqueData);
        });
    });
}

function downloadCSV(data) {
    const csvContent = data.map(e => e.join(",")).join("\n");
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const downloadLink = document.getElementById('downloadLink');
    downloadLink.href = url;
    downloadLink.download = 'unique_data.csv';
    downloadLink.style.display = 'block';
    downloadLink.textContent = '結果をダウンロード';
}