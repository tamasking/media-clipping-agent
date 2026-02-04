import React from 'react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { Calendar, MessageSquare, Repeat } from 'lucide-react';

const TaskCard = ({ task }) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging
  } = useSortable({ id: task.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  const priorityColors = {
    low: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
    medium: 'bg-accent-orange/20 text-accent-orange border-accent-orange/30',
    high: 'bg-accent-purple/20 text-accent-purple border-accent-purple/30',
    critical: 'bg-red-500/20 text-red-400 border-red-500/30',
  };

  const typeIcons = {
    health_check: '💜',
    backup: '📋',
    monitoring: '📊',
    custom: '📝',
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      className="bg-dark-700 rounded-lg p-4 border border-white/5 hover:border-accent-cyan/30 transition-all cursor-grab active:cursor-grabbing mb-3"
    >
      <div className="flex items-start gap-3 mb-3">
        <span className="text-lg">{typeIcons[task.task_type] || '📝'}</span>
        <div className="flex-1">
          <h4 className="text-sm font-medium text-white mb-1">{task.title}</h4>
          <p className="text-xs text-gray-400 line-clamp-2">{task.description}</p>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 mb-3">
        <span className={`text-xs px-2 py-0.5 rounded-full border ${priorityColors[task.priority] || priorityColors.medium}`}>
          {task.priority}
        </span>
        {task.is_recurring > 0 && (
          <span className="text-xs px-2 py-0.5 rounded-full bg-accent-cyan/10 text-accent-cyan border border-accent-cyan/20 flex items-center gap-1">
            <Repeat className="w-3 h-3" />
            Recurring
          </span>
        )}
      </div>

      <div className="flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center gap-1">
          <MessageSquare className="w-3 h-3" />
          <span>0</span>
        </div>
        <div className="flex items-center gap-1">
          <Calendar className="w-3 h-3" />
          <span>{formatDate(task.created_at)}</span>
        </div>
      </div>
    </div>
  );
};

export default TaskCard;
