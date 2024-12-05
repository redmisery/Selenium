function getLocalFormattedDate(date) {
  // 格式化为本地时间 YYYY-MM-DD HH:mm:ss
  return date.toLocaleString('en-CA', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
    hour12: false // 24小时制
  }).replace(/\//g, '-').replace(',', '');
}

// 获取当前时间
var nowTime = new Date();
// beginTime为昨天的日期
var beginTime = new Date(nowTime.getTime() - 24 * 60 * 60 * 1000);
// endTime在beginTime基础上加10分钟
var endTime = new Date(beginTime.getTime() + 10 * 60 * 1000);
beginTime = getLocalFormattedDate(beginTime);
endTime = getLocalFormattedDate(endTime);

pm.variables.set('beginTime', beginTime);
pm.variables.set('endTime', endTime);