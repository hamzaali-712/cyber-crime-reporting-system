import { cn } from '@/lib/utils';
import type { ComplaintStatus } from '@/lib/database.types';
import { STATUS_CONFIG } from '@/lib/database.types';

interface BadgeProps {
  status: ComplaintStatus;
  className?: string;
}

export function StatusBadge({ status, className }: BadgeProps) {
  const config = STATUS_CONFIG[status];
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
        config.bgClass,
        config.textClass,
        className,
      )}
    >
      <span
        className="mr-1.5 h-1.5 w-1.5 rounded-full"
        style={{ backgroundColor: config.color }}
      />
      {config.label}
    </span>
  );
}

interface GenericBadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'secondary' | 'success' | 'warning' | 'danger' | 'info' | 'outline';
}

const badgeVariants = {
  default: 'bg-blue-500/10 text-blue-700',
  secondary: 'bg-gray-100 text-gray-700',
  success: 'bg-green-500/10 text-green-700',
  warning: 'bg-amber-500/10 text-amber-700',
  danger: 'bg-red-500/10 text-red-700',
  info: 'bg-cyan-500/10 text-cyan-700',
  outline: 'bg-transparent border border-gray-200 text-gray-600',
};

export function Badge({ variant = 'default', className, ...props }: GenericBadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
        badgeVariants[variant],
        className,
      )}
      {...props}
    />
  );
}
