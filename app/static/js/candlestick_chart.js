document.addEventListener('DOMContentLoaded', function() {
    // var plotData = {{ plot_data | tojson | safe }};
    
    var traceBitcoin = {
        x: plotData.x.filter((_, i) => plotData.crypto[i] === 'bitcoin'),
        open: plotData.open.filter((_, i) => plotData.crypto[i] === 'bitcoin'),
        high: plotData.high.filter((_, i) => plotData.crypto[i] === 'bitcoin'),
        low: plotData.low.filter((_, i) => plotData.crypto[i] === 'bitcoin'),
        close: plotData.close.filter((_, i) => plotData.crypto[i] === 'bitcoin'),
        type: 'candlestick',
        name: 'Bitcoin',
        xaxis: 'x',
        yaxis: 'y'
    };

    var traceEthereum = {
        x: plotData.x.filter((_, i) => plotData.crypto[i] === 'ethereum'),
        open: plotData.open.filter((_, i) => plotData.crypto[i] === 'ethereum'),
        high: plotData.high.filter((_, i) => plotData.crypto[i] === 'ethereum'),
        low: plotData.low.filter((_, i) => plotData.crypto[i] === 'ethereum'),
        close: plotData.close.filter((_, i) => plotData.crypto[i] === 'ethereum'),
        type: 'candlestick',
        name: 'Ethereum',
        xaxis: 'x2',
        yaxis: 'y2'
    };

    var traceTether = {
        x: plotData.x.filter((_, i) => plotData.crypto[i] === 'tether'),
        open: plotData.open.filter((_, i) => plotData.crypto[i] === 'tether'),
        high: plotData.high.filter((_, i) => plotData.crypto[i] === 'tether'),
        low: plotData.low.filter((_, i) => plotData.crypto[i] === 'tether'),
        close: plotData.close.filter((_, i) => plotData.crypto[i] === 'tether'),
        type: 'candlestick',
        name: 'Tether',
        xaxis: 'x2',
        yaxis: 'y2'
    };

    var layout = {
        title: 'Cryptocurrency Price Comparison',
        grid: {rows: 2, columns: 1, pattern: 'independent'},
        xaxis: {title: 'Date'},
        yaxis: {title: 'Bitcoin Price (USD)', range: [40000, 75000]},
        xaxis2: {title: 'Date'},
        yaxis2: {title: 'Other Prices (USD)', range: [0, 10000]},
        xaxis: {
            rangeslider: { visible: false },
            tickformat: '%m-%d',
            tickmode: 'auto',
            nticks: 30,
            tickangle: -45,
            showticklabels: false
        },
        xaxis2: {
            rangeslider: { visible: false },
            tickformat: '%m-%d',
            tickmode: 'auto',
            nticks: 30,
            tickangle: -45
        },
    };

    var data = [traceBitcoin, traceEthereum, traceTether];

    Plotly.newPlot('candlestick-chart', data, layout);
});
