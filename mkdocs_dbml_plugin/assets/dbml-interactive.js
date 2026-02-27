document.addEventListener('DOMContentLoaded', function() {
    const diagrams = document.querySelectorAll('.dbml-diagram');
    
    diagrams.forEach(diagram => {
        let scale = 1;
        let isPanning = false;
        let startX = 0;
        let startY = 0;
        let translateX = 0;
        let translateY = 0;
        
        const wrapper = diagram.closest('.dbml-diagram-wrapper');
        
        diagram.addEventListener('mousedown', (e) => {
            if (e.target.closest('.dbml-table-group')) return;
            isPanning = true;
            startX = e.clientX - translateX;
            startY = e.clientY - translateY;
            diagram.style.cursor = 'grabbing';
        });
        
        document.addEventListener('mousemove', (e) => {
            if (!isPanning) return;
            translateX = e.clientX - startX;
            translateY = e.clientY - startY;
            diagram.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`;
        });
        
        document.addEventListener('mouseup', () => {
            isPanning = false;
            diagram.style.cursor = 'grab';
        });
        
        diagram.addEventListener('wheel', (e) => {
            e.preventDefault();
            const delta = e.deltaY > 0 ? 0.9 : 1.1;
            scale *= delta;
            scale = Math.max(0.5, Math.min(scale, 2));
            diagram.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`;
        });
        
        const tableGroups = diagram.querySelectorAll('.dbml-table-group');
        tableGroups.forEach(group => {
            group.addEventListener('click', () => {
                const tableName = group.getAttribute('data-table');
                highlightRelatedTables(diagram, tableName);
            });
        });
    });
    
    function highlightRelatedTables(diagram, tableName) {
        const allGroups = diagram.querySelectorAll('.dbml-table-group');
        const allLines = diagram.querySelectorAll('.dbml-relationship-line');
        
        allGroups.forEach(g => {
            const rect = g.querySelector('.dbml-table-bg');
            if (g.getAttribute('data-table') === tableName) {
                rect.setAttribute('stroke', '#6366f1');
                rect.setAttribute('stroke-width', '4');
            } else {
                rect.setAttribute('stroke', '#e5e7eb');
                rect.setAttribute('stroke-width', '2');
            }
        });
        
        allLines.forEach(line => {
            line.setAttribute('opacity', '0.3');
        });
    }
});
