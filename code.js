/*初期化*/
function initialize() {
    var spreadSheet = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = spreadSheet.getSheetByName('一覧');
    sheet.getRange('C6:C200').removeCheckboxes();     //チェックボックスの削除
    sheet.getRange('H6:H200').clearContent();     //通知ステータスの内容削除
    var data_num = sheet.getRange('F2').getValue();
    var row;
    for (var i=0;i<data_num;i++) {
      row = i + 6;
      sheet.getRange(`C${row}`).insertCheckboxes();     //チェックボックス挿入
            sheet.getRange(`H${row}`).setValue(`=IF($F${row}="","",IF($C${row}=TRUE,"非通知",IF($G${row}="終了",,IF(VALUE($G${row})>VALUE(TIME(0,16,0)),"未通知",IF($H${row}="通知済","通知済","通知待")))))`);     //通知ステータスの数式入力
    }
    if(sheet.getFilter() !== null){
      sheet.getFilter().remove();     //フィルターの削除
    }
    sheet.getRange(`$C5:$H${data_num+5}`).createFilter();     //フィルター作成
    async function setTrigger(){
      await deleteTriggers();
      setRefleshTrigger();
    }
    setTrigger();
  }
  
  function setRefleshTrigger() {
    ScriptApp.newTrigger("reflesh")
    .timeBased()
    .everyMinutes(1)
    .create();
  }
  
  function deleteTriggers() {
    var triggers = ScriptApp.getProjectTriggers();     //すべてのトリガーを取得
    //トリガーを削除
    for(var trigger of triggers){    
      if(trigger.getHandlerFunction() == "reflesh"){
  　　　// 見つかったら消す
        ScriptApp.deleteTrigger(trigger);
      }
    } 
  }
  
  /*LINEに通知を送信（checkAlert()から呼び出し）*/
  function sendAlert(place,round,time) {
    var message = `締切15分前\n${place} ${round}R 締切時刻：${time}`;
    var token = ["UZJlK53WTN2PxRxNqhT5kfQGgZBpPdXmYE9RhwjBJ72"];
    const url = "https://notify-api.line.me/api/notify";
    const params = {
      "method":"post",
      "payload":{"message":message},
      "headers":{"Authorization":"Bearer " + token}
    };
    UrlFetchApp.fetch(url,params);
  }
  
  /*通知を送るレースがないか確認（reflesh()から呼び出し）*/
  function checkAlert(sheet){
    var data_num = sheet.getRange('F2').getValue();
    var row;
    for (var i=0;i<data_num;i++) {
      row = i + 6;
      status = sheet.getRange(`H${row}`).getValue();
      if(status === "通知待"){
        place = sheet.getRange(`D${row}`).getValue();
        round = sheet.getRange(`E${row}`).getValue();
        time = sheet.getRange(`F${row}`).getValue();
        sendAlert(place,round,time);
        sheet.getRange(`H${row}`).setValue(`=IF($F${row}="","",IF($G${row}="終了","","通知済"))`);
      }
    }
  }
  
  /*再計算（毎分トリガーから呼び出し）*/
  function reflesh(){
    var spreadSheet = SpreadsheetApp.openById('1R2fPel8-r6A1jsg2i90TxK2RHmki_zl2GKzJvx2q-rU');
    var sheet = spreadSheet.getSheetByName('一覧');
    sheet.getRange('A200').setValue('foo');  // A1セルに'foo'と入力
    sheet.getRange('A200').setValue('');
    SpreadsheetApp.flush();  // 変更内容を即反映
    checkAlert(sheet);
    test();
  }
  